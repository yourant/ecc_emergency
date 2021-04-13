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
import os
import json
import requests
from apps.lens import lens
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from apps.emergency.models import EmergencyOmnibus, EmergencyOvertime, choices, EmergencyOvertimeGroup, \
    EmergencyOmnibusGroup

from blueapps.conf.default_settings import APP_CODE, BASE_DIR

ip_path = os.path.join(BASE_DIR, "home_application\ip_sys.json")


# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
# FLAG = True


def home(request):
    """
    首页
    """
    # global FLAG
    # if FLAG:
    #     print('import consume', FLAG)
    #     from apps.emergency.kafkadata import consume
    #     FLAG = False
    # else:
    #     print(FLAG)
    return render(request, 'home_application/index.html')


def dev_guide(request):
    """
    开发指引
    """
    return render(request, 'home_application/dev_guide.html')


def contact(request):
    """
    联系页
    """
    return render(request, 'home_application/contact.html')


def more_msg(request):
    try:
        group_obj = request.GET.get("table").lower()
        group_id = request.GET.get("id")
        print(group_id,group_obj,"787878")
        table = {"EmergencyOvertimeGroup":EmergencyOvertimeGroup,"EmergencyOmnibusGroup":EmergencyOmnibusGroup}
        model_overtime = lens._registry.get(table[group_obj])
        response = model_overtime._api(method='GET', data={})
        table_data = ""
        ip = ""
        system = ""
        # print(response,4567766)
        if response.get('code') == 1:
            data = response.get('data').get('items')
            # print(data)
            for item in data:

                if item['id'] == int(group_id) and group_obj == "EmergencyOmnibusGroup":
                    table_data = item
                    system = item['system_cn']
                    #print(item['summary'].split("\\n"),89089)
                    ip = item['summary'].split("\\n")[1]
                elif item['id'] == group_id:
                    table_data = item
                    system = item['system_cn']
                    ip = ""
                    break
        all_data = {}
        all_data["data"] = table_data
        system_dict = {}
        datly = ""
        url = "http://102.150.5.19:90/api/Flow/BaseFlowSyncData"
        data = {"TableID": "08"}
        response = requests.post(url=url, data=data)
        ret = json.loads(response.text)
        ret = json.loads(ret["Data"])
        # ret = [{"BillNo":"ba3443542525424","Detailed":"系统今天宕机需要重启","ToSystem":"一体化运维系统","ChgExecPerson":"刘三","JiHuaKaiShiShiJian":"2020-12-03 10:10:45","JiHuaJieShuShiJian":"2020-12-03 21:10:45","SSStateStr":"已完成","FlowName":"实施"},{"BillNo":"ba3443542525424","Detailed":"系统今天宕机需要重启","ToSystem":"手机银行系统","ChgExecPerson":"刘三","JiHuaKaiShiShiJian":"2020-12-03 10:10:45","JiHuaJieShuShiJian":"2020-12-03 21:10:45","SSStateStr":"已完成","FlowName":"实施"},{"BillNo":"ba3443542525424","Detailed":"系统今天宕机需要重启","ToSystem":"网银系统","ChgExecPerson":"刘三","JiHuaKaiShiShiJian":"2020-12-03 10:10:45","JiHuaJieShuShiJian":"2020-12-03 21:10:45","SSStateStr":"已完成","FlowName":"实施"}]
        try:
            for i in ret:
                if system == i["ToSystem"]:
                    print(111)
                    datly = i
                else:
                    pass
            if datly:
                pass
            else:
                print(333)
                datly = "今日该系统没有变更"
        except:
            print(44444)
            datly = "今日该系统没有变更"
        all_data['itil'] = datly
        # 根据id查询当前告警信息，并获取到该条告警信息的summry。并分割获取ip,查询相应的系统。
        print(ip,system,5656)
        if ip:
            # with open('ip_sys.json', "r") as f:
            with open(ip_path, "r") as f:
                ip_sys = json.load(f)
            s_li = []
            for i in ip_sys[ip.strip()]:
                s_li.append(i.strip())
            for i in s_li:
                if system == i:
                    s_li.remove(system)
                    print(s_li,8989)
                    system_dict[system] = s_li
                    break
        else:
            system_dict[system] = "暂无数据"
        all_data['system'] = system_dict
    except:
        print('报错！！！！')
        return "信息错误"
    # all_data = {'data': {'emergencyomnibus': [], 'id': 1, 'event': '无法处理的字段:event, 错误:Event matching query does not exist.', 'status': 1, 'storage_datetime': None, 'system_cn': '手机银行系统', 'occurrence_time': None, 'summary': '的联发科\\n102.200.206.40', 'contact': 'sd', 'level': 10}, 'itil': {'BillNo': 'ba3443542525424', 'Detailed': '系统今天宕机需要重启', 'ToSystem': '手机银行系统', 'ChgExecPerson': '刘三', 'JiHuaKaiShiShiJian': '2020-12-03 10:10:45', 'JiHuaJieShuShiJian': '2020-12-03 21:10:45', 'SSStateStr': '已完成', 'FlowName': '实施'}, 'system': ['手机银行系统','招聘管理系统', '集中银联前置系统', '资产负债管理系统', '作业调度', '安全蜜罐系统']}
    all_data['data_finish'] = {}
    return JsonResponse(all_data)
