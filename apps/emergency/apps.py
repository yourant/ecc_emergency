import os

from django.apps import AppConfig

from config import IS_USE_APSCHEDULER


class EmergencyConfig(AppConfig):
    name = 'apps.emergency'
    verbose_name = '告警监控'
    info = {
        'description': '基于Django2.0+框架开发，结合规则引擎APP定义的规则，对相关系统实时推送的数据进行格式校验、聚合、展示、通知、处理、储存、导出。',
        'features': [
            '对相关系统实时推送的数据入库储存前进行格式校验、聚合的统一化处理。',
            '结合规则引擎APP定义的规则对输入的元数据实时构建动态规则，生成可用于Django框架的高级Q查询对象，对数据库内已经持久化的数据进行聚合匹配。',
            '数据大屏展示与前端二次处理。',
            '下发企业微信通知。',
            '关联处理人。',
            '数据导出。'
        ],
        'reference': [
            ('Django', 'https://docs.djangoproject.com/zh-hans/2.0/'),
            ('requests', 'https://rulez.readthedocs.io/'),
            ('kafka', 'https://rulez.readthedocs.io/'),
            ('xlwt', 'https://rulez.readthedocs.io/'),
            ('celery', 'https://rulez.readthedocs.io/'),
            ('redis', 'https://rulez.readthedocs.io/'),
            ('dwebsocket', 'https://rulez.readthedocs.io/'),
            ('APScheduler', 'https://rulez.readthedocs.io/'),
        ],
        'big_show': '/bigshow'
    }

    def ready(self):
        # print('RUN_MAIN', os.environ.get('RUN_MAIN', None))
        # print('environ', os.environ)
        import apps.emergency.signals

        # 区分主进程/daemon进程
        if os.environ.get('RUN_MAIN', None) == 'true':
            # import apps.emergency.kafkadata.consume
            import apps.emergency.task

            if IS_USE_APSCHEDULER:
                # from django.utils.module_loading import autodiscover_modules
                # autodiscover_modules('schedule')
                import apps.emergency.schedules
