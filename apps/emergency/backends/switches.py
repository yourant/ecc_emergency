import requests
import json

from config import CMDB, ITIL


class Itil(object):
    """Itil系统的人员信息接口"""
    __url = ITIL.get('url')

    def __init__(self):
        super(Itil, self).__init__()

    @classmethod
    def get_contact(cls):
        '''
        获取itil中所有人员信息
        '''
        itil_staff_url = "https://paas.hxtest.com/api/c/compapi/ecc_emergency/get_itil_staff_info/"
        data = {
            "bk_app_code": "ecc_emergency",
            # FIXME: 生产上需要使用新建应用的bk_app_secret
            "bk_app_secret": "0a07f710-7c5e-40ec-891b-fdb204282047",
            "bk_username": "admin"
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url=itil_staff_url, data=json.dumps(
            data), verify=False, headers=headers)
        return json.loads(json.loads(response.text)["data"])


class Cmdb(object):
    """CMDB"""
    __url = CMDB.get('url')

    def __init__(self):
        super(Cmdb, self).__init__()

    @property
    @classmethod
    def token(cls):
        '''获取token
        '''
        result = requests.get(url=cls.url + 'sso.do?username=cmdbUser')
        return result.text

    @classmethod
    def get_system_name(cls, system_id):
        '''
        根据system_id从cmdb中获取系统名称
        '''

        url = cls.url + 'hdcaintf/cmdbData.do?ApiToken={}'.format(token)
        data = {
            "Class": "DC_ApplicationSystem",
            "Action": "GET",
            "contiditon": "applicationSystemId={}".format(system_id),
            "content": ""
        }
        data = json.dumps(data)
        res = requests.post(url=url, data=data)
        result = json.loads(res.text)
        return result["Content"]['bodyList'][0]['NAME']


class Esdb(object):
    """elastic search databash 数据存取"""

    def __init__(self, arg):
        super(Esdb, self).__init__()
        self.arg = arg
