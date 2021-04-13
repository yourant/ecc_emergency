import time
import zlib
import base64
import json

from django.http import JsonResponse
from dwebsocket.decorators import accept_websocket
from kafka import KafkaConsumer, TopicPartition

from config import KAFKA, QUEUE_TEST

from apps.lens import lens, utils
from apps.emergency import models


@accept_websocket
def kafka(request):
    '''kafka取值并实时通过websocket推送到前端测试

    [description]

    Decorators:
        accept_websocket

    Arguments:
        request {[type]} -- [description]
    '''
    print('ws request', request, dir(request))

    consumer = KafkaConsumer(KAFKA.get('topics')[0],
                             auto_offset_reset='latest',
                             bootstrap_servers=[
                             KAFKA.get('host') + ':' + KAFKA.get('port')])

    for msg in consumer:
        print(msg)
        data = msg.value
        data = zlib.decompress(base64.b64decode(data))
        data = data.decode('utf-8')
        print(data)
        # 发送消息到客户端
        request.websocket.send(bytes(data, encoding='utf-8'))


@accept_websocket
def kafka_seek(request):
    '''kafka指定offset取值并实时通过websocket推送到前端测试

    [description]

    Decorators:
        accept_websocket

    Arguments:
        request {[type]} -- [description]
    '''
    print('ws request', request, dir(request))

    # 若使用seek 则生成consumer对象不能传入topics等值
    consumer = KafkaConsumer(bootstrap_servers=[
        KAFKA.get('host') + ':' + KAFKA.get('port')]
    )

    # 注册TopicPartition
    tp = TopicPartition(KAFKA.get('topics')[0], 0)
    consumer.assign([tp])

    # 定位到指定offset
    consumer.seek(tp, 4850)

    # 循环取值
    for msg in consumer:
        print(msg)
        data = msg.value
        # 解码 配合生产环境
        data = zlib.decompress(base64.b64decode(data))
        data = data.decode('utf-8')
        print(data)
        # 发送消息到客户端
        request.websocket.send(bytes(data, encoding='utf-8'))


@accept_websocket
def allgroup(request):
    '''数据变动时通过消息队列主动向前端推送 测试接口
    '''

    while True:
        # if QUEUE_OMNIBUS.empty():
        #     continue
        data = QUEUE_TEST.get()
        # print('Ws emergencyovertimegroup data', type(data))
        if not type(data) == str:
            data = json.dumps(data)
        request.websocket.send(bytes(data, encoding='utf-8'))
        # time.sleep(3)


def emergencyovertime(request):
    '''测试接口
    
    [description]
    
    Arguments:
        request {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    '''
    data = {
        "is_checkbox": True,
        "hash_id": "123456qwert",
        # "group_id": 1,
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
    # print('emergencyovertime response', response)
    return JsonResponse(response, json_dumps_params={'ensure_ascii': False},)


def fault(request):
    '''故障定位 测试接口
    '''
    data = {
    "items": [
        {
          "chartLinks": [
          {
            "des": "3",
            "source": "华夏生产环境\n集中采购系统\n集中采购供应商门户应用服务器2\n102.200.202.222",
            "target": "中金机房\nPC服务器\n102.200.205.75",
            "type": 0
          },
          {
            "des": "3",
            "source": "华夏生产环境\n集中采购系统\n集中采购管理系统应用服务器2\n102.200.202.220",
            "target": "中金机房\nPC服务器\n102.200.205.75",
            "type": 0
          },
          {
            "des": "3",
            "source": "华夏生产环境\n集中采购系统\n集中采购数据库服务器2\n102.200.202.224",
            "target": "中金机房\nPC服务器\n102.200.205.75",
            "type": 0
          }],
          "alarmDes":
          {
            "des": "09:47:05 集中采购系统有2台机器重启,IP为102.200.202.220,102.200.202.222.请确认集中采购系统是否在做变更或着演练."
          },
          "alarmY":
          {
            "startTime": "2020-10-13 09:43:00",
            "qcnname": "华夏生产环境:集中采购系统:集中采购供应商门户应用服务器2:102.200.202.222;华夏生产环境:集中采购系统:集中采购管理系统应用服务器2:102.200.202.220;华夏生产环境:集中采购系统:集中采购数据库服务器2:102.200.202.224",
            "des": "09:47:05 集中采购系统有2台机器重启,IP为102.200.202.220,102.200.202.222.请确认集中采购系统是否在做变更或着演练.",
            "name": "虚拟机批量重启,物理机可能出现异常",
            "number": "3",
            "type": "资源类",
            "sysname": "中金机房:PC服务器:102.200.205.75"
          },
          "time":
          {
            "time2": "2020-10-13 09:43:00",
            "time1": "2020-10-13 09:43:00",
            "isover": "True"
          },
          "tradeBlock": [],
          "chartNodes": [
          {
            "category": 1,
            "des": "中金机房\nPC服务器\n102.200.205.75",
            "name": "中金机房\nPC服务器\n102.200.205.75",
            "type": 4,
            "symbolSize": 100
          },
          {
            "category": 1,
            "des": "",
            "name": "华夏生产环境\n集中采购系统\n集中采购供应商门户应用服务器2\n102.200.202.222",
            "type": 2,
            "symbolSize": 30
          },
          {
            "category": 1,
            "des": "",
            "name": "华夏生产环境\n集中采购系统\n集中采购管理系统应用服务器2\n102.200.202.220",
            "type": 2,
            "symbolSize": 30
          },
          {
            "category": 1,
            "des": "",
            "name": "华夏生产环境\n集中采购系统\n集中采购数据库服务器2\n102.200.202.224",
            "type": 0,
            "symbolSize": 30
          }],
          "overtimeData": [],
          "types": "omnibus",
          "tradeTotal": "",
          "serial": "1",
          "resouceData": [
          {
            "summary": "集中采购数据库服务器2:delay_check1,当前指标值(661.0) 大于等于 (600.0);HXB_EVENT_ZH_BK\n 102.200.202.224",
            "remark": "系统室石晓东告知物理机宕机导致，无影响",
            "mastertid": "",
            "event_id": "",
            "effectnum": "否",
            "type": "数据库",
            "ttime": "09:52:07",
            "contact": "系统负责人:王志刚:13911073832,",
            "dealer": "",
            "timestamp": "1602555512.136",
            "id": "125840",
            "operation": "其他",
            "tally": "",
            "swapiden": "HXB_EVENT_ZH_BK",
            "ntlogged": "",
            "lastoccurrence": "1602553860",
            "dep": "9999",
            "event_count": "",
            "firstoccurrence": "1602553860",
            "is_release": "无",
            "status": "1",
            "group_id": "1602555502",
            "severity": "5",
            "flag1": "1",
            "servername": "bluekingmonitor",
            "url": "20",
            "operator": "",
            "jyresult": "",
            "system": "集中采购系统",
            "node": "102.200.202.224",
            "statechange": "1602553927",
            "acknowledged": "",
            "start_time": "10:18:32",
            "identifier": ""
          },
          {
            "summary": "集中采购数据库服务器2:keepalived进程监控,当前指标值(0) = (0.0);HXB_EVENT_ZH_BK\n 102.200.202.224",
            "remark": "系统室石晓东告知物理机宕机导致，无影响",
            "mastertid": "",
            "event_id": "",
            "effectnum": "否",
            "type": "数据库",
            "ttime": "09:47:05",
            "contact": "系统负责人:王志刚:13911073832,",
            "dealer": "",
            "timestamp": "1602555512.136",
            "id": "125835",
            "operation": "其他",
            "tally": "",
            "swapiden": "HXB_EVENT_ZH_BK",
            "ntlogged": "",
            "lastoccurrence": "1602553440",
            "dep": "9999",
            "event_count": "",
            "firstoccurrence": "1602553440",
            "is_release": "无",
            "status": "1",
            "group_id": "1602555502",
            "severity": "5",
            "flag1": "1",
            "servername": "bluekingmonitor",
            "url": "20",
            "operator": "",
            "jyresult": "",
            "system": "集中采购系统",
            "node": "102.200.202.224",
            "statechange": "1602553625",
            "acknowledged": "",
            "start_time": "10:18:32",
            "identifier": ""
          },
          {
            "summary": "集中采购数据库服务器2:keepalived进程监控,当前指标值(0) < (3.0);HXB_EVENT_ZH_BK\n 102.200.202.224",
            "remark": "系统室石晓东告知物理机宕机导致，无影响",
            "mastertid": "",
            "event_id": "",
            "effectnum": "否",
            "type": "数据库",
            "ttime": "09:47:05",
            "contact": "系统负责人:王志刚:13911073832,",
            "dealer": "",
            "timestamp": "1602555512.136",
            "id": "125836",
            "operation": "其他",
            "tally": "",
            "swapiden": "HXB_EVENT_ZH_BK",
            "ntlogged": "",
            "lastoccurrence": "1602553440",
            "dep": "9999",
            "event_count": "",
            "firstoccurrence": "1602553440",
            "is_release": "无",
            "status": "1",
            "group_id": "1602555502",
            "severity": "5",
            "flag1": "1",
            "servername": "bluekingmonitor",
            "url": "20",
            "operator": "",
            "jyresult": "",
            "system": "集中采购系统",
            "node": "102.200.202.224",
            "statechange": "1602553625",
            "acknowledged": "",
            "start_time": "10:18:32",
            "identifier": ""
          },
          {
            "summary": "集中采购数据库服务器2:slave线程,当前指标值(0) < (2.0);HXB_EVENT_ZH_BK\n 102.200.202.224",
            "remark": "系统室石晓东告知物理机宕机导致，无影响",
            "mastertid": "",
            "event_id": "",
            "effectnum": "否",
            "type": "数据库",
            "ttime": "09:47:05",
            "contact": "系统负责人:王志刚:13911073832,",
            "dealer": "",
            "timestamp": "1602555512.136",
            "id": "125837",
            "operation": "其他",
            "tally": "",
            "swapiden": "HXB_EVENT_ZH_BK",
            "ntlogged": "",
            "lastoccurrence": "1602553440",
            "dep": "9999",
            "event_count": "",
            "firstoccurrence": "1602553440",
            "is_release": "无",
            "status": "1",
            "group_id": "1602555502",
            "severity": "5",
            "flag1": "1",
            "servername": "bluekingmonitor",
            "url": "20",
            "operator": "",
            "jyresult": "",
            "system": "集中采购系统",
            "node": "102.200.202.224",
            "statechange": "1602553625",
            "acknowledged": "",
            "start_time": "10:18:32",
            "identifier": ""
          },
          {
            "summary": "集中采购数据库服务器2:mysqld启动时间,当前指标值(188.0) <= (300.0);HXB_EVENT_ZH_BK\n 102.200.202.224",
            "remark": "系统室石晓东告知物理机宕机导致，无影响",
            "mastertid": "",
            "event_id": "",
            "effectnum": "否",
            "type": "数据库",
            "ttime": "09:47:05",
            "contact": "系统负责人:王志刚:13911073832,",
            "dealer": "",
            "timestamp": "1602555512.136",
            "id": "125838",
            "operation": "其他",
            "tally": "",
            "swapiden": "HXB_EVENT_ZH_BK",
            "ntlogged": "",
            "lastoccurrence": "1602553500",
            "dep": "9999",
            "event_count": "",
            "firstoccurrence": "1602553500",
            "is_release": "无",
            "status": "1",
            "group_id": "1602555502",
            "severity": "5",
            "flag1": "1",
            "servername": "bluekingmonitor",
            "url": "20",
            "operator": "",
            "jyresult": "",
            "system": "集中采购系统",
            "node": "102.200.202.224",
            "statechange": "1602553625",
            "acknowledged": "",
            "start_time": "10:18:32",
            "identifier": ""
          },
          {
            "summary": "集中采购管理系统应用服务器2:系统重新启动,当前服务器(102.200.202.220)发生系统重启事件;HXB_EVENT_ZH_BK\n 102.200.202.220",
            "remark": "系统室石晓东告知物理机宕机导致，无影响",
            "mastertid": "",
            "event_id": "",
            "effectnum": "否",
            "type": "数据库",
            "ttime": "09:46:07",
            "contact": "系统负责人:王志刚:13911073832,",
            "dealer": "",
            "timestamp": "1602555512.136",
            "id": "125833",
            "operation": "其他",
            "tally": "",
            "swapiden": "HXB_EVENT_ZH_BK",
            "ntlogged": "",
            "lastoccurrence": "1602553380",
            "dep": "9999",
            "event_count": "",
            "firstoccurrence": "1602553380",
            "is_release": "无",
            "status": "1",
            "group_id": "1602555502",
            "severity": "5",
            "flag1": "1",
            "servername": "bluekingmonitor",
            "url": "20",
            "operator": "",
            "jyresult": "",
            "system": "集中采购系统",
            "node": "102.200.202.220",
            "statechange": "1602553567",
            "acknowledged": "",
            "start_time": "10:18:32",
            "identifier": ""
          }],
          "nameNodes": "华夏生产环境\n集中采购系统\n集中采购供应商门户应用服务器2\n102.200.202.222\n华夏生产环境\n集中采购系统\n集中采购管理系统应用服务器2\n102.200.202.220\n华夏生产环境\n集中采购系统\n集中采购数据库服务器2\n102.200.202.224\n"
        },
        {
          "chartLinks": [
          {
            "des": "100.00%",
            "source": "综合前置系统",
            "target": "互联网营销活动支持系统(渠道)",
            "type": 0
          },
          {
            "des": "0%",
            "source": "综合前置系统",
            "target": "柜面系统(渠道)",
            "type": 0
          },
          {
            "des": "100.00%",
            "source": "综合前置系统",
            "target": "手机银行系统(服务)",
            "type": 1
          }],
          "alarmDes":
          {
            "des": "11:33:58至11:41:00   互联网营销活动支持、柜面2个渠道到手机银行系统的手机银行加挂账户信息查询等3笔交易发生异常.故障定位为手机银行系统故障.故障期间交易成功率为99.73%.",
            "flag": "0"
          },
          "alarmY":
          {
            "startTime": "2020-10-13 11:33:58",
            "qcnname": "互联网营销活动支持系统;柜面系统",
            "des": "11:33:58至11:41:00   互联网营销活动支持、柜面2个渠道到手机银行系统的手机银行加挂账户信息查询等3笔交易发生异常.故障定位为手机银行系统故障.故障期间交易成功率为99.73%.",
            "name": "手机银行系统",
            "number": "3",
            "type": "交易类",
            "sysname": "综合前置系统"
          },
          "time":
          {
            "time2": "2020-10-13 11:41:00",
            "time1": "2020-10-13 11:33:58",
            "isover": "True"
          },
          "tradeBlock": [
          {
            "id": "0",
            "count": "3",
            "name": "手机银行系统",
            "type": "1"
          }],
          "chartNodes": [
          {
            "category": 1,
            "des": "综合前置系统",
            "name": "综合前置系统",
            "type": 1,
            "symbolSize": "3"
          },
          {
            "category": 1,
            "des": "互联网营销活动支持系统(渠道)",
            "name": "互联网营销活动支持系统(渠道)",
            "type": 0,
            "symbolSize": "3"
          },
          {
            "category": 1,
            "des": "柜面系统(渠道)",
            "name": "柜面系统(渠道)",
            "type": 0,
            "symbolSize": "0"
          },
          {
            "category": 1,
            "des": "手机银行系统(服务)",
            "name": "手机银行系统(服务)",
            "type": 2,
            "symbolSize": "3|100"
          }],
          "overtimeData": [
          {
            "count": "",
            "remark": "吴晶晶告知3笔无影响，超时属于闪断在重新做一次就可以，在报再联系",
            "event_id": "",
            "id": "73",
            "timestamp": "1602560443.405",
            "dealer": "",
            "qudao": "WEBMARKCLI",
            "qudaocn": "互联网营销平台系统",
            "key": "zjapp009-localin-20201013113233-563281",
            "branch_cn": "总行",
            "flag4": "无",
            "system_group": "",
            "end_time_group": "",
            "status": "1",
            "group_id": "1602560434",
            "code": "S000303001322:手机银行加挂账户信息查询",
            "flag3": "否",
            "sever": "MBPHSVR",
            "flag2": "查询超时",
            "system": "综合前置",
            "end_time": "11:33:43",
            "route": "",
            "rtcode_cn": "ESB-E-000052:超时未得到服务系统应答",
            "sever_cn": "手机银行系统",
            "start_time": "11:33:34",
            "error_count": "3",
            "start_time_group": "11:40:43"
          }],
          "types": "trade",
          "tradeTotal": "3",
          "serial": "2119",
          "resouceData": [],
          "nameNodes": "互联网营销活动支持系统\n柜面系统\n"
        },
        {
          "chartLinks": [
          {
            "des": "100.00%",
            "source": "综合前置系统",
            "target": "影像前端系统(渠道)",
            "type": 0
          },
          {
            "des": "0%",
            "source": "综合前置系统",
            "target": "柜面系统(渠道)",
            "type": 0
          },
          {
            "des": "100.00%",
            "source": "综合前置系统",
            "target": "BEAI系统(服务)",
            "type": 1
          }],
          "alarmDes":
          {
            "des": "11:38:58至11:41:00   影像前端、柜面2个渠道到BEAI系统的S001303002451等3笔交易发生异常.故障定位为BEAI系统故障.故障期间交易成功率为99.96%.",
            "flag": "0"
          },
          "alarmY":
          {
            "startTime": "2020-10-13 11:38:58",
            "qcnname": "影像前端系统;柜面系统",
            "des": "11:38:58至11:41:00   影像前端、柜面2个渠道到BEAI系统的S001303002451等3笔交易发生异常.故障定位为BEAI系统故障.故障期间交易成功率为99.96%.",
            "name": "BEAI系统",
            "number": "3",
            "type": "交易类",
            "sysname": "综合前置系统"
          },
          "time":
          {
            "time2": "2020-10-13 11:40:46",
            "time1": "2020-10-13 11:38:58",
            "isover": "True"
          },
          "tradeBlock": [
          {
            "id": "0",
            "count": "3",
            "name": "BEAI系统",
            "type": "1"
          }],
          "chartNodes": [
          {
            "category": 1,
            "des": "综合前置系统",
            "name": "综合前置系统",
            "type": 1,
            "symbolSize": "3"
          },
          {
            "category": 1,
            "des": "影像前端系统(渠道)",
            "name": "影像前端系统(渠道)",
            "type": 0,
            "symbolSize": "3"
          },
          {
            "category": 1,
            "des": "柜面系统(渠道)",
            "name": "柜面系统(渠道)",
            "type": 0,
            "symbolSize": "0"
          },
          {
            "category": 1,
            "des": "BEAI系统(服务)",
            "name": "BEAI系统(服务)",
            "type": 2,
            "symbolSize": "3|100"
          }],
          "overtimeData": [
          {
            "count": "",
            "remark": "无",
            "event_id": "",
            "id": "69",
            "timestamp": "1602561192.171",
            "dealer": "",
            "qudao": "ABSCOMCLI",
            "qudaocn": "影像前端系统",
            "key": "zjapp007-localin-20201013110726-348807",
            "branch_cn": "总行",
            "flag4": "无",
            "system_group": "",
            "end_time_group": "",
            "status": "1",
            "group_id": "1602561182",
            "code": "S001303002450:S001303002450",
            "flag3": "否",
            "sever": "NBEAISVR",
            "flag2": "查询超时",
            "system": "综合前置",
            "end_time": "11:43:19",
            "route": "",
            "rtcode_cn": "ESB-E-000052:超时未得到服务系统应答",
            "sever_cn": "BEAI系统",
            "start_time": "11:08:27",
            "error_count": "6",
            "start_time_group": "11:53:12"
          }],
          "types": "trade",
          "tradeTotal": "3",
          "serial": "2120",
          "resouceData": [],
          "nameNodes": "影像前端系统\n柜面系统\n"
        },
        {
          "chartLinks": [
          {
            "des": "100.00%",
            "source": "综合前置系统",
            "target": "影像前端系统(渠道)",
            "type": 0
          },
          {
            "des": "100.00%",
            "source": "综合前置系统",
            "target": "同城票据交换系统(服务)",
            "type": 1
          }],
          "alarmDes":
          {
            "des": "12:23:28至12:35:19   影像前端渠道到同城票据交换系统的业务查询分页等20笔交易发生异常.故障定位为同城票据交换系统故障.故障期间交易成功率为70.15%.",
            "flag": "0"
          },
          "alarmY":
          {
            "startTime": "2020-10-13 12:23:28",
            "qcnname": "影像前端系统",
            "des": "12:23:28至12:35:19   影像前端渠道到同城票据交换系统的业务查询分页等20笔交易发生异常.故障定位为同城票据交换系统故障.故障期间交易成功率为70.15%.",
            "name": "同城票据交换系统",
            "number": "20",
            "type": "交易类",
            "sysname": "综合前置系统"
          },
          "time":
          {
            "time2": "2020-10-13 12:35:05",
            "time1": "2020-10-13 12:23:28",
            "isover": "True"
          },
          "tradeBlock": [
          {
            "id": "0",
            "count": "20",
            "name": "同城票据交换系统",
            "type": "1"
          }],
          "chartNodes": [
          {
            "category": 1,
            "des": "综合前置系统",
            "name": "综合前置系统",
            "type": 1,
            "symbolSize": "20"
          },
          {
            "category": 1,
            "des": "影像前端系统(渠道)",
            "name": "影像前端系统(渠道)",
            "type": 0,
            "symbolSize": "20"
          },
          {
            "category": 1,
            "des": "同城票据交换系统(服务)",
            "name": "同城票据交换系统(服务)",
            "type": 2,
            "symbolSize": "20|100"
          }],
          "overtimeData": [
          {
            "count": "",
            "remark": "无",
            "event_id": "",
            "id": "77",
            "timestamp": "1602567020.247",
            "dealer": "",
            "qudao": "ABSCOMCLI",
            "qudaocn": "影像前端系统",
            "key": "dbapp007-localin-20201013123226-049418",
            "branch_cn": "北京分行",
            "flag4": "无",
            "system_group": "",
            "end_time_group": "",
            "status": "1",
            "group_id": "1602567010",
            "code": "S001303001018:业务查询分页",
            "flag3": "否",
            "sever": "NCPESSVR",
            "flag2": "查询超时",
            "system": "综合前置",
            "end_time": "12:33:05",
            "route": "",
            "rtcode_cn": "SC000010017:接收节点网络不通",
            "sever_cn": "同城票据交换系统",
            "start_time": "12:32:26",
            "error_count": "5",
            "start_time_group": "13:30:20"
          },
          {
            "count": "",
            "remark": "告知可能分行有柜员不会操作导致，无影响，会直接联系北京分行进行告知",
            "event_id": "",
            "id": "74",
            "timestamp": "1602563307.05",
            "dealer": "",
            "qudao": "ABSCOMCLI",
            "qudaocn": "影像前端系统",
            "key": "dbapp007-localin-20201013122317-039713",
            "branch_cn": "北京分行",
            "flag4": "无",
            "system_group": "",
            "end_time_group": "",
            "status": "1",
            "group_id": "1602563297",
            "code": "S001303001018:业务查询分页",
            "flag3": "否",
            "sever": "NCPESSVR",
            "flag2": "查询超时",
            "system": "综合前置",
            "end_time": "12:24:14",
            "route": "",
            "rtcode_cn": "SC000010017:接收节点网络不通",
            "sever_cn": "同城票据交换系统",
            "start_time": "12:23:17",
            "error_count": "12",
            "start_time_group": "12:28:27"
          }],
          "types": "trade",
          "tradeTotal": "20",
          "serial": "2121",
          "resouceData": [],
          "nameNodes": "影像前端系统\n"
        }]
    }
    return JsonResponse(
        utils.ApiResponse(code=1, msg='成功', data=data).__dict__,
        json_dumps_params={'ensure_ascii': False},
        )