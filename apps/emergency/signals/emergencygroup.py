"""
Desc: 告警监控App告警聚合表增删改查阶段钩子
"""
from django.dispatch import receiver
from django.db.models import signals
# from django.core.signals import request_started, request_finished

from apps.emergency import models
from apps.emergency.backends import EmergencyMQ, Notify

from apps.lens import lens, logger
# from config import logger


# @receiver(signals.pre_init, sender=models.EmergencyOmnibusGroup)
# @receiver(signals.pre_init, sender=models.EmergencyOvertimeGroup)
# def pre_init(*args, **kwargs):
#     '''
#     构造model对象前
#     '''
#     logger.info('signals(pre_init)接收到了一条(%s)数据' % sender,)


@receiver(lens.post_before, sender=models.EmergencyOmnibusGroup)
@receiver(lens.post_before, sender=models.EmergencyOvertimeGroup)
def post_before(sender, request, **kwargs):
    '''新增数据前
    '''
    logger.info('signals(post_before)接收到了一条(%s)数据' % sender,)


@receiver(signals.post_init, sender=models.EmergencyOmnibusGroup)
@receiver(signals.post_init, sender=models.EmergencyOvertimeGroup)
def post_init(instance, **kwargs):
    '''新增数据前
    '''
    # 数据更新前 记录下老数据的status
    instance.old_status = instance.status
    # logger.info('Group post_init', instance.old_status, instance.status)


@receiver(lens.patch_before, sender=models.EmergencyOmnibusGroup)
@receiver(lens.patch_before, sender=models.EmergencyOvertimeGroup)
def patch_before(sender, request, instance, **kwargs):
    '''PATCH方法下修改一条数据并且未经modelform校验之前
    '''
    logger.info('signals(patch_before)接收到了一条(%s)数据' % sender,)

    # 审查notify_list合规性 若有notify_list 校验其保证格式为list
    notify_list = request.data.get('notify_list', [])
    if notify_list:
        if type(notify_list) != list:
            raise Exception('字段(notify_list)类型请确保是列表/数组(list/array)')

    # 差集 比较是否有非法的通知方法名
    invalid = set(notify_list) - set({'wecom_appchat', 'wecom_message'})
    # logger.info('invalid', invalid)
    if invalid:
        raise Exception('参数(notify_list)中有非法的通知方法名(%s)' % str(invalid))

    # 审查event合规性
    if request.data.get('event'):
        event_dict = request.data.pop('event')
        if event_dict:
            # 若前端仍有传值但已关联事件
            if not (type(event_dict) == dict):
                raise Exception('event必须为一个dict / object')
            if instance.event:
                raise Exception('当前告警聚合已经关联事件%s, 请勿再次关联' %
                                instance.event)

            # 将event的数据追加到instance 交由valid_after阶段处理
            # 避开event这个属性名的原因当时未备注 现在忘记了
            instance.event_dict = event_dict


@receiver(lens.valid_after, sender=models.EmergencyOmnibusGroup)
@receiver(lens.valid_after, sender=models.EmergencyOvertimeGroup)
def valid_after(sender, request, instance, **kwargs):
    '''modelform校验之后存库前(这个钩子函数本身不区分request.method 请手动区分)
    '''
    logger.info('signals(valid_after)',)

    def create_event(data):
        '''创建事件
        params:
            data: dict, 创建event的元数据
        return: int, 已创建event的id
        '''

        model_obj = lens._registry.get(models.Event)
        response = model_obj._api('post', data)
        # logger.info('Group valid_after response', response)
        if response.get('code') == 1:
            event_pk = response.get('data').get('pk')
            return models.Event.objects.get(pk=event_pk)
        else:
            raise Exception(str(response.get('data')))

    if request.method == 'PATCH':
        # status = request.data.get('status', '')
        # if instance.old_status == 0 and status == 1:
        #     logger.info('已通知', )

        # elif instance.old_status == 1 and status == 2:
        #     logger.info('已处理', )

        # 传入元数据中若有event的数据则生成事件并关联之
        if hasattr(instance, 'event_dict'):
            event_pk = create_event(instance.event_dict)
            logger.info('event_pk', event_pk)
            instance.event = event_pk

# @receiver(signals.pre_save, sender=models.EmergencyOmnibusGroup)
# # def emergencyomnibusgroup_pre_save(instance, **kwargs):
# def pre_save(instance, raw, using, update_fields, **kwargs):
#     '''
#     综告警聚合(Group)某一条数据存库前
#     '''
#     pass


# @receiver(signals.post_save, sender=models.EmergencyOmnibusGroup)
# # def emergencyomnibusgroup_pre_save(instance, **kwargs):
# def post_save(instance, created, **kwargs):
@receiver(lens.patch_save, sender=models.EmergencyOmnibusGroup)
@receiver(lens.patch_save, sender=models.EmergencyOvertimeGroup)
def patch_save(sender, request, instance, **kwargs):
    '''PATCH数据存库后
    params: 
        instance: object, model_group对象
        notify_list: list, 通知名称列表
    '''
    logger.info('signals(patch_save)',)

    # 向前端Websocket推送数据的mq中推送数据
    EmergencyMQ.send(sender)

    # 校验发送企业通知的通知用户列表(dealer_list)
    if hasattr(instance, 'event_dict'):
        dealer_list = instance.event_dict.get('dealer_list', [])
    else:
        dealer_list = []
    # logger.info('dealer_list', dealer_list)

    # 获取通知名称列表并调用Notify
    try:
        notify_list = request.data.get('notify_list', [])
        Notify.dispatch(instance, notify_list, dealer_list=dealer_list)
    except Exception as e:
        logger.exception('[调用Notify] - ', e)
        raise Exception(e)

# @receiver(lens.post_before, sender=models.EmergencyOmnibusGroup)
# def post_before(sender, **kwargs):
#     '''在新增一条数据之前
#     '''
#     pass
