import os

from django.apps import AppConfig

from config.dev import DEBUG


class LensConfig(AppConfig):
    name = 'apps.lens'

    def ready(self):
        # 当程序启动时 去每个app目录下找lens.py并加载
        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('lens')

        # 区分主进程/daemon进程
        if os.environ.get('RUN_MAIN', None) == 'true':
            if DEBUG:
                print('\033[0;31m!!!在生产环境部署本项目请将config.dev中DEBUG设置为False\033[0m')
