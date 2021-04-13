# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from __future__ import absolute_import

import os

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from blueapps.core.celery import celery_app

__all__ = ['celery_app', 'RUN_VER', 'APP_CODE',
           'SECRET_KEY', 'BK_URL', 'BASE_DIR']


# app 基本信息


def get_env_or_raise(key):
    """Get an environment variable, if it does not exist, raise an exception
    """
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(
            ('Environment variable "{}" not found, you must set this variable to run this application.'
             ).format(key)
        )
    return value


# SaaS运行版本，如非必要请勿修改
RUN_VER = 'open'
# SaaS应用ID
APP_CODE = 'bk_ecc_emergency'
# SaaS安全密钥，注意请勿泄露该密钥
SECRET_KEY = '5103a2e7-2733-4a02-aebf-157f80fe508f'
# 蓝鲸SaaS平台URL，例如 http://paas.bking.com
# BK_URL = 'https://paas.hxmis.com:443'  # 生产环境URL
# BK_URL = 'https://paas.hxtest.com:443'  # 测试环境URL
BK_URL = 'https://localhost:8000'  # 开发环境

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(
    __file__)))


# 自定义全局配置
# APSCHEDULER 任务调度器开关，使用时请改为 True
IS_USE_APSCHEDULER = True

# kafka
KAFKA = {
    # 'broker_list': ['102.104.88.50:9092', '102.104.88.51:9092', '102.104.88.52:9092', '102.104.88.53:9092',
    #                 '102.104.88.54:9092'],  # 生产环境
    'broker_list': ['192.168.43.126:19092'],  # 开发环境
    'topics': ['HXB_Event_Omnibus_Group', 'HXB_Event_Overtime_Group']
}

# 向前端实时推送消息的消息队列
import queue

QUEUE_EMERGENCYOMNIBUSGROUP = queue.Queue(maxsize=30)
QUEUE_EMERGENCYOVERTIMEGROUP = queue.Queue(maxsize=30)
QUEUE_TEST = queue.Queue(maxsize=30)

# WeCom企业微信
# 蓝鲸生产配置
# WECOM = {
#     'url': 'http://103.160.52.66:13082/',
#     'corpid': 'ww8e033a26be886631',
#     'corpsecret': 'XvlXnz2CMHG99vp99Sg3B3-145d8v7vvsDk9JNr_89U',
#     'chatid': 1234567892,
#     'msgtype': 'markdown',
#     'msgtype': 'textcard'
# }

# 蓝鲸测试配置
# WECOM = {
#     'url': 'http://103.160.52.66:13082/',
#     'corpid': 'ww8e033a26be886631',
#     'corpsecret': 'XvlXnz2CMHG99vp99Sg3B3-145d8v7vvsDk9JNr_89U',
#     'chatid': 1234567892,
#     'msgtype': 'markdown',
#     'msgtype': 'textcard'
# }

# 公网测试配置
WECOM = {
    'url': 'https://qyapi.weixin.qq.com/',
    'corpid': 'ww49e307cd2251093c',
    'corpsecret': '3IA7nbHCsoqlRFPHWsdO1HlfUV3XgD1b0yXLn7G81WU',
    # 'chatid': 'wriGCRCwAAjGCeaKHK7EMb5bwFhGQOKg',   # 火星小分队
    'chatid': 'wriGCRCwAACZkFkCVoTCXFiL9F3eaIzA',   # 个人
    # 'msgtype': 'text',
    # 'msgtype': 'markdown',
    'msgtype': 'textcard',
    'agentid': 1000004
}

WECOM_MSG_TYPE_CLASS = {
    'text': 'apps.emergency.plugins.wecommsg.Text',
    'textcard': 'apps.emergency.plugins.wecommsg.TextCard',
    'markdown': 'apps.emergency.plugins.wecommsg.MarkDown',
}

# Itil
ITIL = {
    'url': 'http://103.160.183.72:90/api/Flow/BaseFlowSyncData',
}

# Cmdb
CMDB = {
    'url': 'http://103.160.103.66:9001/hdca/',
}

# Esdb

# 部署主机地址
DEPLOY_HOST = 'http://127.0.0.1:8000'  # 本地测试
# DEPLOY_HOST = 'http://paas.hsmix.com/o/bk_ecc_emergency'  # 生产
