"""
Desc: 规则引擎App表操作钩子函数
"""
from django.dispatch import receiver
from django.db.models import signals

from apps.lens import lens
from apps.lens.utils import logger, decorator
from apps import ruler


@receiver(lens.post_before, sender=ruler.models.EmergencyOmnibusRule)
@receiver(lens.post_before, sender=ruler.models.EmergencyOvertimeRule)
def post_before(sender, request, **kwargs):
    '''在新增一条数据之前
    '''
    rule = request.data.get('rule')
    logger.info('signals(post_before)接收到了一条(%s)数据' % sender,
                # type(rule),
                # rule,
                )

    # 校验rule合法性
    result_valid = ruler.ruler.verify_rule(rule)
    logger.info('signals(post_before) rule合法性结果(%s)' %
                # type(result_valid),
                result_valid,
                )
    if not result_valid:
        raise Exception('rule不合法')


# @receiver(lens.valid_after, sender=ruler.models.EmergencyOmnibusRule)
# def valid_after(sender, request, instance, **kwargs):
#     '''PATCH方法下修改一条数据并且经modelform校验之后
#     '''
#     logger.info('阶段(%s valid_after)' % sender,
#                 # sender, request, instance,
#                 # kwargs
#                 )


# @receiver(lens.pre_save, sender=ruler.models.EmergencyOmnibusRule)
# def pre_save(instance, **kwargs):
#     '''数据存库前
#     '''


# @receiver(signals.post_save, sender=ruler.models.EmergencyOmnibusRule)
# def post_save(sender, instance, **kwargs):
#     '''POST方法下数据存库后
#     '''
#     logger.info('阶段(%s post_save)' % sender)


# @receiver(lens.patch_before, sender=ruler.models.EmergencyOmnibusRule)
# def patch_before(sender, request, instance, **kwargs):
#     '''PATCH方法下数据存库后
#     '''
#     logger.info('阶段(%s patch_before)' % sender,)


# @receiver(request_started)
# def request_started(sender, **kwargs):
#     '''
#     '''


# @receiver(request_finished)
# def request_finished(sender, **kwargs):
#     '''
#     '''
#     logger.info('emergencyomnibus_request_finished', kwargs)
