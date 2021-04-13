import base64
import hashlib
import json
import os
import time
import zlib
from datetime import datetime, timedelta

from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from django.views import View
from kafka import KafkaConsumer, TopicPartition, OffsetAndMetadata

from apps.emergency.kafkadata.models import FaultLocation
from apps.emergency.models import EmergencyOmnibus, EmergencyOvertime, choices, EmergencyOvertimeGroup, \
    EmergencyOmnibusGroup
from apps.emergency.models.emergency import ImportantSystem
from apps.lens import lens
from config import KAFKA


def consumer_poll(request):
    topics = KAFKA.get('topics')
    broker_list = KAFKA.get('broker_list')
    consumer = KafkaConsumer(
        bootstrap_servers=broker_list,
        group_id='api_data_poll',
        consumer_timeout_ms=20000,
    )
    data = {}
    for topic in topics:
        partitions = consumer.partitions_for_topic(topic)
        print('主题%s对应分区为%s' % (topic, partitions))
        for partition in partitions:
            tp = TopicPartition(topic, partition)
            consumer.assign([tp])
            print(consumer.end_offsets([tp]))
            # print(consumer.position(tp))
            # consumer.seek_to_end(tp)
            # offset = int(consumer.end_offsets([tp]).get(tp)) - 1
            # consumer.seek(tp, offset)
            msg = consumer.poll(timeout_ms=1000)
            consumer.commit()
            data_key = str(topic) + '-' + str(partition)
            if not msg:
                data[data_key] = msg
            else:
                record_list = msg.get(tp)
                # print('**********', len(record_list))
                data_value = {}
                for record in record_list:
                    record_key = str(record.topic) + '-' + str(record.partition) + '-' + str(record.offset)
                    if not os.getenv('BK_ENV'):
                        data_list = eval(zlib.decompress(base64.b64decode(record.value)).decode('gbk'))
                    else:
                        data_list = json.loads(zlib.decompress(base64.b64decode(record.value)).decode('gbk'))
                    record_value = {}
                    for index, item in enumerate(data_list):
                        if not item.get('children'):
                            record_value[index] = item
                            key_format = str(index) + '-format'
                            hash_id = hashlib.md5(str(item).encode(encoding='UTF-8')).hexdigest()
                            params = {'hash_id': hash_id}
                            if item.get('summary'):
                                for key, value in item.items():
                                    if key in EmergencyOmnibus._meta.field_map.keys():
                                        params[EmergencyOmnibus._meta.field_map.get(key)] = value
                                    else:
                                        params[key] = value
                                params['operation'] = int(
                                    [choice[0] for choice in choices.get('EmergencyOmnibus_opration') if
                                     choice[1] == params['operation']][0])
                                params['level'] = '0' if params['level'] not in {'10', '20', '40', '50'} else params[
                                    'level']
                                record_value[key_format] = params
                            if item.get('key'):
                                for key, value in item.items():
                                    if key in EmergencyOvertime._meta.field_map.keys():
                                        params[EmergencyOvertime._meta.field_map.get(key)] = value
                                    else:
                                        params[key] = value
                                code_code_cn = params.pop('code')
                                rtcode_rtcode_cn = params.pop('rtcode_cn')
                                params['code'] = code_code_cn.split(':')[0]
                                params['code_cn'] = code_code_cn.split(':')[1]
                                params['rtcode'] = rtcode_rtcode_cn.split(':')[0]
                                params['rtcode_cn'] = rtcode_rtcode_cn.split(':')[1]
                                record_value[key_format] = params
                    data_value[record_key] = record_value
                data[data_key] = data_value
    response = {
        "code": 1,
        "msg": 'success',
        "data": data
    }
    return JsonResponse(response)
    # return render(request, 'emergency/data/poll.html', context={'response': response})


# 交易类
def overtime(request):
    # q = request.GET.get("q")
    # status = request.GET.get("status")
    model_overtime = lens._registry.get(EmergencyOvertimeGroup)
    response = model_overtime._api(method='GET', data={})
    # response = model_overtime._api(method='GET', data={"q":q,"status":status})
    if response.get('code') == 1:
        data = response.get('data').get('items')
        # for item in data[::-1]:
            # if item['status'] != int(status):
            #     data.remove(item)
        return JsonResponse(response)
    else:
        print(response)
        return JsonResponse(response)


# 综合类
def omnibus(request):
    # q = request.GET.get("q")
    # status = request.GET.get("status")
    # print(q, '888')
    model_omnibus = lens._registry.get(EmergencyOmnibusGroup)
    response = model_omnibus._api(method='GET', data={})
    # response = model_omnibus._api(method='GET', data={"q":q,"status":status})
    if response.get('code') == 1:
        data = response.get('data').get('items')
        print(type(data),'66666')
        for item in data[::-1]:
            item['color'] = 'green'
            if int(item['level']) == 50:
                item['color'] = 'yellow'
            if item['system_cn'] in ImportantSystem:
                item['color'] = 'red'
            # if item['status'] != int(status):
            #     data.remove(item)
        # print(data)
        return JsonResponse(response)
        # new_response = {'code': response['code'], 'msg': response['msg']}
        # data = response['data']
        # new_data = {
        #     'table': data['table'],
        #     'label': data['label'],
        #     'fields': data['fields'],
        #     'render_items': data['items'],
        # }
        # new_response['data'] = new_data
        # return render(request, 'emergency/data/show.html', context={'response': new_response})
    else:
        print(response)
        return JsonResponse(response)


# 故障定位
def fault_location(request):
    now = datetime.now()
    before_now = now + timedelta(days=-1)
    fault_locations = FaultLocation.objects.filter(time_into_db__lte=now, time_into_db__gte=before_now)
    # print(fault_locations)
    li = []
    for fault in fault_locations:
        li.append(eval(fault.value))
    data_list = sorted(li, key=lambda i: (i['id'], i['statechange']), reverse=True)
    ids = [data['id'] for data in data_list]
    id_list = list(set(ids))
    id_list.sort(key=ids.index)
    items = []
    for id_value in id_list:
        for data in data_list:
            if data['id'] == id_value:
                items.append(data)
                break
    if items:
        response = {'code': 1, 'msg': 'success', 'data': {'items': items}}
        return JsonResponse(response)
    else:
        response = {'code': 1, 'msg': 'success', 'data': {'items': li}}
        return JsonResponse(response)


def handle_database(request):
    query_dict = request.GET
    sql = query_dict.get('sql')
    table = query_dict.get('table')
    table_dict = {
        'jy': 'emergency_emergencyovertime',
        'jyg': 'emergency_emergencyovertimegroup',
        'zh': 'emergency_emergencyomnibus',
        'zhg': 'emergency_emergencyomnibusgroup',
        'fl': 'emergency_faultlocation',
        'djc_c': 'djcelery_crontabschedule',
        'djc_i': 'djcelery_intervalschedule',
        'djc_p': 'djcelery_periodictask',
        'djc_ps': 'djcelery_periodictasks',
        'djc_t': 'djcelery_taskstate',
        'djc_w': 'djcelery_workerstate',
    }
    table_name = table_dict.get(table)
    with connection.cursor() as cursor:
        if sql == 'select':
            cursor.execute(f"select * from {table_name};")
            columns = [col[0] for col in cursor.description]
            response = [dict(zip(columns, row)) for row in cursor.fetchall()]
        elif sql == 'delete':
            cursor.execute(f"delete from {table_name};")
            row = cursor.fetchone()
            response = row
    # return JsonResponse({"res": response})
    return HttpResponse(response)
