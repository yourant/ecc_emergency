import os

from django.apps import AppConfig


class RulerConfig(AppConfig):
    name = 'apps.ruler'
    verbose_name = '规则引擎'
    info = {
        'description': '基于Rulez二次开发的、可融合进Django2.0+的、可在前端配置的规则引擎。',
        'features': [
            '根据静态规则对输入的数据进行过滤。',
            '根据输入的元数据实时构建动态规则，对输入的数据进行过滤。',
            '根据输入的元数据实时构建动态规则，生成可用于Django框架的高级Q查询对象，对数据库内已经持久化的数据进行匹配查询。',
            '使用JSON格式对规则进行描述、构建、储存，因此可支持用户使用包括网页前端在内的终端，进行规则创建与编辑。',
            '支持DSL(Domain Specified Language)领域专用语言。',
        ],
        'reference': [
            ('Django', 'https://docs.djangoproject.com/zh-hans/2.0/'),
            ('Rulez', 'https://rulez.readthedocs.io/'),
            ('jsonfield', 'https://rulez.readthedocs.io/'),
            ('formio', 'https://rulez.readthedocs.io/'),
        ],
    }

    def ready(self):

        import apps.ruler.signals

        # import apps.ruler.ruler
        # import apps.ruler.durable
        # import apps.ruler._engine
        # import apps.ruler._business_rules
        # import apps.ruler.core
        # import apps.ruler._lens
        # 区分主进程/daemon进程
        if os.environ.get('RUN_MAIN', None) == 'true':
            pass
