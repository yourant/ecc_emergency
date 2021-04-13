"""
Desc: 告警监控App告警表增删改查阶段钩子
"""
import json
import time

from django.dispatch import receiver
from django.db.models import signals
# from django.core.signals import request_started, request_finished

from apps.emergency import models
from apps.emergency.backends import EmergencyMQ

from apps.lens import lens
from apps.lens.utils import logger, decorator
from apps import ruler
# from config import logger
# from blueapps.utils.logger import logger


# logger.debug('logger ....... debug')
# logger.info('logger ....... info')
# logger.warning('logger ....... warning')
# logger.error('logger ....... error')
# logger.critical('logger ....... critical')

mapping_model = {
    models.EmergencyOmnibus: {
        'rule': ruler.models.EmergencyOmnibusRule,
        'group': models.EmergencyOmnibusGroup,
    },
    models.EmergencyOvertime: {
        'rule': ruler.models.EmergencyOvertimeRule,
        'group': models.EmergencyOvertimeGroup,
    },
}


@receiver(lens.post_before, sender=models.EmergencyOmnibus)
@receiver(lens.post_before, sender=models.EmergencyOvertime)
def post_before(sender, request, **kwargs):
    '''新增数据前
    '''
    logger.info('signals(post_before)接收到了一条(%s)数据' % sender,)
    group = request.data.get('group')
    if group:
        raise Exception(
            '字段(group)由系统聚合规则自动匹配关联 暂不允许用户主动指定 发送POST请求时请勿定义此字段')

    # 临时增加 以经过校验
    # request.data['group'] = 1


@receiver(lens.patch_before, sender=models.EmergencyOmnibus)
@receiver(lens.patch_before, sender=models.EmergencyOvertime)
def patch_before(sender, request, instance, **kwargs):
    '''新增数据前
    '''
    logger.info('signals(patch_before)')
    if request.data.get('group'):
        raise Exception(
            '字段(group)由系统聚合规则自动匹配关联 暂不允许用户主动修改 发送PPTCH请求时请勿定义此字段')


@receiver(lens.valid_after, sender=models.EmergencyOmnibus)
@receiver(lens.valid_after, sender=models.EmergencyOvertime)
def valid_after(sender, request, instance, **kwargs):
    '''modelform校验之后存库前(这个钩子函数本身不区分request.method 请手动区分)
    '''
    logger.info('signals(valid_after)',)
    model_group = mapping_model.get(sender).get('group')

    # 告警表元数据注入group的fileds_func映射
    mapping_fileds_func = {
        models.EmergencyOmnibusGroup: {
            'status': 0,
            'storage_datetime': time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(float(request.data.get('storage_timestamp')))),
            'level': request.data.get('level', 10),
        },
        models.EmergencyOvertimeGroup: {
            'status': 0,
            'storage_datetime': time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(float(request.data.get('storage_timestamp')))),
        },
    }

    def inject_fields():
        '''根据告警表元数据构造group的post数据
        '''
        data = {}
        for field in model_group._meta.fields:
            func = mapping_fileds_func[model_group].get(field.name)
            # logger.info('lambda_func func --------', field.name, func)
            if func == None:
                # logger.info('lambda_func func if', func, request.data.get(field.name))
                data[field.name] = request.data.get(field.name)
            else:
                # logger.info('lambda_func func else', func)
                data[field.name] = func
        return data

    def create_group():
        '''根据告警元数据创建一条新的聚合数据
        '''
        lens_model = lens._registry.get(model_group)
        data = inject_fields()
        response = lens_model._api('post', data)
        # logger.info('create_group data response', data, response)
        if response.get('code') == 1:
            group_pk = response.get('data').get('pk')
            logger.info('成功创建了一条聚合数据(%s)(%s)' % (sender, group_pk))
            return model_group.objects.get(pk=group_pk)
        else:
            raise Exception('valid_after钩子函数阶段 创建聚合数据失败(%s)' % str(sender))

    def get_aggregate_group():
        '''根据聚合规则获取匹配到的group 无匹配结果则返回新创建的group
        '''
        # logger.info('get_aggregate_group')
        model_rule = mapping_model.get(sender).get('rule')

        # 查询聚合规则
        instance_rule_list = model_rule.objects.filter(is_enable=True)
        if len(instance_rule_list):
            # 合并规则
            rule = {"operator": "and", "value": []}
            for instance_rule in instance_rule_list:
                rule['value'].extend(instance_rule.rule.get('value', []))
            # logger.info('rule', rule['value'])
            # 匹配聚合规则
            result = ruler.ruler.filter(
                rule, instance, filter_model=model_group)

            if result != None:
                logger.info(
                    '聚合规则(%s)匹配到了一条已有的告警聚合数据(%s)' % (instance_rule, result.pk))
                return result

        logger.info(
            '(%s)表中无规则或无处于启用状态的规则, 或未匹配到已有的告警聚合数据' % (model_rule,))
        return create_group()

    if request.method == 'POST':
        # 根据规则进行group的关联或创建关联
        instance.group = get_aggregate_group()
        logger.info('将当前告警纳入到聚合数据(%s)' % instance.group.pk)


# @receiver(signals.pre_save, sender=models.EmergencyOmnibus)
# @receiver(signals.pre_save, sender=models.EmergencyOvertime)
# def pre_save(instance, **kwargs):
#     '''
#     综合类告警(EmergencyOmnibus)某一条数据存库前
#     对比status字段是否有更新
#     若有更新则根据关联的事件(Event)发送企业微信通知
#     若尚未关联的事件(Event)则生成一条新的事件(Event)进行关联 并发送企业微信通知
#     '''


@receiver(signals.post_save, sender=models.EmergencyOmnibus)
@receiver(signals.post_save, sender=models.EmergencyOvertime)
def post_save(sender, instance, **kwargs):
    '''POST数据存库后
    '''

    logger.info('signals(post_save)', )

    # 向前端Websocket推送数据的mq中推送数据
    EmergencyMQ.send(mapping_model.get(sender).get('group'))


# @receiver(request_started)
# def request_started(sender, **kwargs):
#     '''
#     '''
#     ret = kwargs.get('environ').get('wsgi.input')
#     ret = str(ret.read())
#     logger.info('emergencyomnibus_request_started',
#           type(ret),
#           ret,
#           # ret.read(),
#           # json.loads()
#           # ret.readline(),
#           # ret.remaining,
#           # ret.stream,
#           )


# @receiver(request_finished)
# def request_finished(sender, **kwargs):
#     '''
#     '''
#     logger.info('emergencyomnibus_request_finished', kwargs)
