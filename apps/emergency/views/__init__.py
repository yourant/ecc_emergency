# import time
import json
import xlwt
from io import BytesIO
from django.views.generic.base import TemplateView
from dwebsocket.decorators import accept_websocket

from apps.emergency.models.emergency import ImportantSystem
from apps.emergency.views import test
from apps.emergency.views import mobile
from django.views import View
from django.http import HttpResponse
from apps.emergency.models.emergency import Employee, System, EmergencyOmnibusGroup, EmergencyOvertimeGroup
from config import KAFKA, QUEUE_EMERGENCYOMNIBUSGROUP, QUEUE_EMERGENCYOVERTIMEGROUP, QUEUE_TEST


class Index(TemplateView):
    template_name = "emergency/frontend/index.html"


class BigShow(TemplateView):
    template_name = "emergency/bigshow/index.html"


class Ws(TemplateView):
    template_name = "emergency/ws/index.html"


@accept_websocket
def emergencyomnibusgroup(request):
    '''数据变动时通过消息队列主动向前端推送
    '''

    while True:
        # if QUEUE_OMNIBUS.empty():
        #     continue
        data = QUEUE_EMERGENCYOMNIBUSGROUP.get()
        # print(type(data))
        # print('Ws emergencyomnibusgroup data', type(data), data)

        if data.get('code') == 1 and data.get('msg') == 'success':
            items = data.get('data').get('items')
            print(items)
            for item in items:
                item['color'] = 'green'
                if int(item['level']) == 50:
                    item['color'] = 'yellow'
                if item['system_cn'] in ImportantSystem:
                    item['color'] = 'red'
            print(items)
        else:
            print('请求失败!')

        if not type(data) == str:
            data = json.dumps(data)

        # print('data', type(data), data)
        request.websocket.send(bytes(data, encoding='utf-8'))
        # time.sleep(3)


@accept_websocket
def emergencyovertimegroup(request):
    '''数据变动时通过消息队列主动向前端推送
    '''

    while True:
        # if QUEUE_OMNIBUS.empty():
        #     continue
        data = QUEUE_EMERGENCYOVERTIMEGROUP.get()
        # print('Ws emergencyovertimegroup data', type(data))
        if not type(data) == str:
            data = json.dumps(data)
        request.websocket.send(bytes(data, encoding='utf-8'))
        # time.sleep(3)


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

class ExportExcel(View):
    def get(self, request):
            ttype = request.GET.get('type', "")
            if ttype == "omnibus":
                history = EmergencyOmnibusGroup.objects.filter(status=2)
            else:
                history = EmergencyOvertimeGroup.objects.filter(status=2)
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment;filename=' + ttype + '.xls'
            if history:
                excel_row = 1
                ws = xlwt.Workbook(encoding='utf-8')
                datastyle = xlwt.XFStyle()
                datastyle.num_format_str = 'yyyy-mm-dd h:mm:ss'
                timestyle = xlwt.XFStyle()
                timestyle.num_format_str = 'h:mm:ss'
                sheet = ws.add_sheet('sheet1')
                if ttype == "omnibus":
                    first_col = sheet.col(2)
                    three_col = sheet.col(3)
                    seven_col = sheet.col(7)
                    eight_col = sheet.col(7)
                    first_col.width = 400 * 20
                    three_col.width = 300 * 20
                    seven_col.width = 200 * 20
                    eight_col.width = 200 * 20
                    sheet.write(0, 0, u'编号')
                    sheet.write(0, 1, u'告警时间')
                    sheet.write(0, 2, u'告警描述')
                    sheet.write(0, 3, u'联系人')
                    sheet.write(0, 4, u'告警分级')
                    sheet.write(0, 5, u'告警状态')
                    sheet.write(0, 6, u'入库时间')
                    sheet.write(0, 7, u'告警系统')
                    for index, item in enumerate(history):
                        sheet.write(excel_row, 0, index)
                        sheet.write(excel_row, 1, item.occurrence_time, timestyle)
                        sheet.write(excel_row, 2, item.summary)
                        sheet.write(excel_row, 3, item.contact)
                        sheet.write(excel_row, 4, item.level)
                        sheet.write(excel_row, 5, item.event)
                        sheet.write(excel_row, 6, item.status)
                        sheet.write(excel_row, 7, item.storage_datetime, datastyle)
                        sheet.write(excel_row, 8, item.system_cn)
                        excel_row += 1
                elif ttype == "overtime":
                    first_col = sheet.col(2)
                    three_col = sheet.col(3)
                    seven_col = sheet.col(7)
                    eight_col = sheet.col(8)
                    first_col.width = 300 * 20
                    three_col.width = 200 * 20
                    seven_col.width = 200 * 20
                    eight_col.width = 200 * 20
                    sheet.write(0, 0, u'编号')
                    sheet.write(0, 1, u'入库时间')
                    sheet.write(0, 2, u'告警系统')
                    sheet.write(0, 3, u'开始时间')
                    sheet.write(0, 4, u'最后时间')
                    sheet.write(0, 5, u'超时数量(笔数)')
                    sheet.write(0, 6, u'渠道翻译')
                    sheet.write(0, 7, u'服务码翻译')
                    sheet.write(0, 8, u'机构码翻译')
                    sheet.write(0, 9, u'交易码')
                    sheet.write(0, 10, u'交易码翻译')
                    sheet.write(0, 11, u'返回码翻译')
                    for index, item in enumerate(history):
                        sheet.write(excel_row, 0, index)
                        sheet.write(excel_row, 1, item.storage_datetime, datastyle)
                        sheet.write(excel_row, 2, item.system_cn)
                        sheet.write(excel_row, 3, item.start_time, timestyle)
                        sheet.write(excel_row, 4, item.end_time, timestyle)
                        sheet.write(excel_row, 5, item.error_count)
                        sheet.write(excel_row, 6, item.qudao_cn)
                        sheet.write(excel_row, 7, item.server_cn)
                        sheet.write(excel_row, 8, item.branch_cn)
                        sheet.write(excel_row, 9, item.code)
                        sheet.write(excel_row, 10, item.code_cn)
                        sheet.write(excel_row, 11, item.rtcode_cn)
                        excel_row += 1
                output = BytesIO()
                ws.save(output)
                output.seek(0)
                response.write(output.getvalue())
            return response

class EmployTelephone(View):
    def get(self, request):
        keyword = request.GET.get('keyword','')
        ret_json = {"employes":[]}
        if not keyword:
            records = Employee.objects.all()
        else:
            records = Employee.objects.filter(StaffName__contains = keyword)
        for item in records:
            employee = {
                "StaffName":"",
                "Mobile":"",
                "OrgName":"",
                "Account":""
            }
            employee["StaffName"] = item.StaffName
            employee["Mobile"] = item.Mobile
            employee["OrgName"] = item.OrgName
            employee["Account"] = item.Account
            ret_json["employes"].append(employee)
        return HttpResponse(json.dumps(ret_json))

class SystemManager(View):
    def get(self, request):
        ret = {
            "staff":[]
        }
        keyword = request.GET.get('keyword', '')
        try:
            system = System.objects.get(name=keyword)
        except:
            return HttpResponse(json.dumps(ret))
        records = system.managers.all()
        for item in records:
            ret["staff"].append({"Account":item.Account, "StaffName":item.StaffName})
        return HttpResponse(json.dumps(ret))