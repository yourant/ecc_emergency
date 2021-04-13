# from django.test import TestCase

# Create your tests here.
from rulez import Engine
from apps.emergency import models
from apps.ruler import ruler
# import dateparser
# import datetime


rule = {'operator': 'and', 'value':
        [
            {
                'field': 'id',
                'operator': '>=',
                'value': 10
                # 'value': {
                #     "operator": "get",
                #     'field': 'id',
                #     'offset': 10,
                # }
            },
            # {
            #     'field': 'system_cn',
            #     'operator': '==',
            #     'value': '系统03',
            #     # 'value': {
            #     #     "operator": "get",
            #     #     'value': 'system_cn',
            #     # }
            # },
            # {'field': 'system_cn', 'operator': '==', 'value': '系统02'},
            {'operator': 'and', 'value':
                [
                    {
                        'field': 'occurrence_time',
                        'operator': '>=',
                        'value': '16:27:47'},
                    {
                        'field': 'occurrence_time',
                        'operator': '<=',
                        'value': '16:35:45'}
                ]
             },
        ]
    }
data = {
            "id": 10,
            "is_checkbox": True,
            "hash_id": "567uhvcdfghu",
            "group": 56,
            "occurrence_time": "01:39:05",
            "storage_timestamp": "1592479851.062",
            "summary": "!!!在生产环境部署本项目请将settings中DEBUG设置为False作业留",
            "mastertid": "告警事件的告警组",
            "contact": "联系人:12345678901,联系人:12345678901,联系人:12345678901,",
            "is_import": True,
            "operation": 1,
            "swapiden": "告警类型",
            "tally": 1,
            "ntlogged": "2",
            "dep": 9999,
            "first_occurrence": "3442371892",
            "last_occurrence": "3242371892",
            "severity": 1,
            "server_name": "告警来源",
            "bapp_system": "告警机器所属系统",
            "level": 10,
            "operator": None,
            "jyresult": None,
            "node": "127.0.0.1",
            "confirm_msg": None,
            "system": "告警系统(来源)",
            "system_cn": "系统02",
            "acknowledged": None,
            "identifier": None
        }

# engine = Engine()
# f = engine.compile_condition('native', rule)
# print(
#     'f',
#     type(f),
#     f,
#     # result.__name__,
#     # dir(result)
# )

# result = f(data)
# print(
#     'result',
#     type(result),
#     result,
#     # result.__name__,
#     # dir(result)
# )

# rule = ruler.build_rule(rule)
# rule = ruler.compile_condition('native', rule)
# rule = ruler.validate_condition(rule)
# rule = QueryAdmin()
# rule.filter_model = models.EmergencyOmnibusGroup

# print(
#     'rule',
#     type(rule),
#     rule,
#     # dir(rule)
# )
# instance = models.EmergencyOmnibus.objects.get(id=1)
# print(
#     'instance',
#     type(instance),
#     instance,
#     # dir(instance)
#     instance.id
# )
res = ruler.filter(rule, data)
print(
    'res',
    type(res),
    res,
    # dir(res)
)



h = {
        "is_enable": True,
        "title": "综合类告警聚合规则1",
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