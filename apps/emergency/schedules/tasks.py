import json
import time
import datetime
import random

from apps.emergency import models
from apps.lens import lens
from apps.lens.utils import logger
from apps import ruler
# from blueapps.utils.logger import logger
from config import KAFKA


def emergencyomnibusrule():
    data = {
        "is_enable": False,
        "title": "综合类告警聚合规则01",
        "describe": "字段(system_cn)相同，且字段(occurrence_time)相差在一分钟内。",
        "rule": {
            "operator": "and",
            "value": [
                {
                    "field": "system_cn",
                    "operator": "==",
                    "value": {
                        "operator": "get",
                        "field": "system_cn"
                    }
                },
                {
                    "operator": "and",
                    "value": [
                        {
                            "field": "occurrence_time",
                            "operator": ">=",
                            "value": {
                                "operator": "get",
                                "field": "occurrence_time",
                                "offset": -60
                            }
                        },
                        {
                            "field": "occurrence_time",
                            "operator": "<=",
                            "value": {
                                "operator": "get",
                                "field": "occurrence_time",
                                "offset": 0
                            }
                        }
                    ]
                }
            ]
        }
    }
    model_obj = lens._registry.get(ruler.models.EmergencyOmnibusRule)
    response = model_obj._api('post', data)
    logger.info('开发环境测试任务在(%s)中插入一条数据 返回结果(%s)' % (
        ruler.models.EmergencyOmnibusRule, response.get('data')))
    return response


def emergencyomnibusrule02():
    data = {
        "is_enable": True,
        "title": "综合类告警聚合规则02",
        "describe": "对字段(system_cn)相同的告警进行聚合",
        "rule": {
            "operator": "and",
            "value": [
                {
                    "field": "system_cn",
                    "operator": "==",
                    "value": {
                        "operator": "get",
                        "field": "system_cn"
                    }
                }
            ]
        }
    }
    model_obj = lens._registry.get(ruler.models.EmergencyOmnibusRule)
    response = model_obj._api('post', data)
    logger.info('开发环境测试任务在(%s)中插入一条数据 返回结果(%s)' % (
        ruler.models.EmergencyOmnibusRule, response.get('data')))
    return response


def emergencyomnibusrule03():
    data = {
        "is_enable": True,
        "title": "综合类告警聚合规则03",
        "describe": "对字段(occurrence_time)相差在一分钟内的告警进行聚合",
        "rule": {
            "operator": "and",
            "value": [
                {
                    "operator": "and",
                    "value": [
                        {
                            "field": "occurrence_time",
                            "operator": ">=",
                            "value": {
                                "operator": "get",
                                "field": "occurrence_time",
                                "offset": -60
                            }
                        },
                        {
                            "field": "occurrence_time",
                            "operator": "<=",
                            "value": {
                                "operator": "get",
                                "field": "occurrence_time",
                                "offset": 0
                            }
                        }
                    ]
                }
            ]
        }
    }
    model_obj = lens._registry.get(ruler.models.EmergencyOmnibusRule)
    response = model_obj._api('post', data)
    logger.info('开发环境测试任务在(%s)中插入一条数据 返回结果(%s)' % (
        ruler.models.EmergencyOmnibusRule, response.get('data')))
    return response


def post_omnibus():
    with open('./docs/data/data_prod_20201119.json', 'r') as f:
        content = json.loads(f.read())
        print('content', type(content), len(content))
        for data in content:
            # print(type(data), data)
            time.sleep(6)

            data = {'hash_id': '456c79cc7475908ddbd8242fcea563eb', 'summary': '事件恢复:核心克隆2机:ITM事件(发生于23:56:12)数据库pcard状态不活动tive_A\n 102.200.162.18', 'mastertid': 'ITM_KRZ_DATABASE_INFORMATION', 'occurrence_time': '23:56:12', 'contact': '系统负责人:3810654810,',
                    'is_import': '否', 'swapiden': 'HXB_KRZ_Database_Inactive_A:pcard:bancsclone2:RZ:pcard:ITM_KRZ_DATABASE_INFORMATION', 'tally': '1024', 'ntlogged': '-1', 'last_occurrence': '1605455652', 'dep': '9999', 'first_occurrence': '1605455652', 'is_checkbox': True, 'severity': '5', 'server_name': 'itm', 'level': '50', 'operator': '', 'jyresult': '', 'system_cn': '核心系统', 'node': '102.200.162.18', 'firm_msg': '', 'storage_timestamp': '1605455772', 'system': '00067', 'acknowledged': '0', 'identifier': ''}

            model_obj = lens._registry.get(models.EmergencyOmnibus)
            response = model_obj._api('post', data)
            print('task post_omnibus', response)
            return response


def emergencyomnibus():
    '''模拟向EmergencyOmnibus表增加一条数据
    提供给celery定时任务调用
    用以在没有kafka数据推送的环境下模拟测试项目整个流程
    '''
    data = {
        "hash_id": "123456qwert",
        "occurrence_time": datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'),
        "summary": "迎春是小狗!",
        "storage_timestamp": "1602479851.062",
        "is_checkbox": True,
        "mastertid": "告警事件的告警组",
        # "contact": "联系人",
        "contact": '操作室值班人员',
        "is_import": True,
        "operation": 1,
        "swapiden": "HXB_123456qwert",
        "tally": 1,
        "ntlogged": 2,
        "dep": 9999,
        "first_occurrence": "1602479551.062",
        "last_occurrence": "1602479857.022",
        "severity": 1,
        "server_name": "告警来源",
        "bapp_system": "告警机器所属系统",
        # "level": 20,
        "operator": "",
        "jyresult": "",
        "node": random.choice(["127.0.0.1", "127.0.0.2", "127.0.0.3"]),
        # "confirm_msg": "告警事件处理信息(预留字段 不建议存值 留空即可）",
        "confirm_msg": None,
        "system": "00338",
        "system_cn": random.choice(['系统01', '系统02', '系统03']),
        "acknowledged": "",
        "identifier": "",
        # "group": "3"
    }

    model_obj = lens._registry.get(models.EmergencyOmnibus)
    response = model_obj._api('post', data)
    logger.info('告警数据(%s)完成所有的处理流程(字段转换-格式校验-聚合匹配-入库-推送到前端), 类型(%s), 返回结果(%s)' %
                (response.get('data').get('pk'), models.EmergencyOmnibus, response.get('msg') if (int(response.get('code'))) else response.get('data')))
    logger.info('-------end--------')
    return response


def emergencyovertime():
    '''模拟向EmergencyOvertime表增加一条数据
    提供给celery定时任务调用
    用以在没有kafka数据推送的环境下模拟测试项目整个流程
    '''
    logger.info('\n阶段(schedule Emergencyovertime post) 开发环境测试任务插入一条数据')
    data = {
        "is_checkbox": True,
        "hash_id": "123456qwert",
        # "group": 1,
        "storage_timestamp": "1602479851.062",
        "start_time": "10:13:00",
        "end_time": "10:23:00",
        "error_count": 121,
        "system": "76290wq",
        "system_cn": "告警渠道(来源)",
        "qudao": "ABSC12345",
        "qudao_cn": "影像前端系统",
        "server": "NBEA123456",
        "server_cn": "BEAI系统",
        "branch_cn": "机构码翻译",
        "code": "S00130123456",
        "code_cn": "交易码翻译S001303123456",
        "rtcode": "ESB-E-123456",
        "rtcode_cn": "超时未得到服务系统应答",
        "key": "dbapp009-rtyu-20201012123456-123456",
        "route": "路由",
        # "contact": "操作室值班人员"
    }

    # response = requests.post(
    #     'http://127.0.0.1:8000/api/v1/emergency/emergencyovertime/',
    #     headers={
    #         'Content-Type': 'application/json',
    #     },
    #     data=json.dumps(data),
    # )
    # return response.json()

    model_obj = lens._registry.get(models.EmergencyOvertime)
    response = model_obj._api('post', data)
    logger.info('开发环境测试任务在(%s)中入库了一条告警数据 返回结果(%s)' %
                (models.EmergencyOvertime, response.get('code') or response.get('data')))
    return response
