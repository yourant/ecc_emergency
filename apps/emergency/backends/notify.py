import requests
import json
import importlib

from apps.emergency import models
from apps.lens import logger
import config
DEBUG = True


class WeCom(object):
    """企业微信
    企业微信的配置位置: config/__init__.WECOM
    部署到生产环境请改配置文件
    """
    __url = config.WECOM.get('url')
    __corpid = config.WECOM.get('corpid')
    __corpsecret = config.WECOM.get('corpsecret')
    __chatid = config.WECOM.get('chatid')
    __msgtype = config.WECOM.get('msgtype')
    __agentid = config.WECOM.get('agentid')

    def __init__(self):
        super(WeCom, self).__init__()

    # @property
    @classmethod
    def token(cls):
        '''获取token
        '''
        params = {
            'corpid': cls.__corpid,
            'corpsecret': cls.__corpsecret,
        }
        response = requests.get(
            url=cls.__url + 'cgi-bin/gettoken', params=params)
        return response.json().get('access_token')

    @classmethod
    def upload_media(cls, media_path, temporary=False):
        '''
        向企业微信上传永久文件并获取调用url
        向企业微信上传临时文件(有效期3天)并获取调用media_id
        Arguments:
            media_path {[Sting]} -- [文件本地路径]
            temporary {[Boolean]} -- [是否上传为临时文件类型]

        Returns:
            [String] -- [临时文件的media_id 或 永久文件的url]

        Raises:
            Exception -- [description]
        '''

        if temporary:  # 临时文件
            placeholder = 'upload'
            result_key = 'media_id'
        else:  # 永久文件？
            placeholder = 'uploadimg'
            result_key = 'url'

        api = cls.__api + 'cgi-bin/media/{}?access_token={}&type=file'.format(
            placeholder,
            cls.token()
        )

        try:
            with open(media_path, "rb") as f:  # 以2进制方式打开图片
                # 上传图片的时候，不使用data和json，用files
                response = requests.post(
                    url=api, files={'file': f}, json=True).json()
        except Exception as e:
            raise Exception('企业微信上传文件时出现错误: %s' % str(e))
        else:
            print('upload_file', response)
            if response.get('errcode') == 0:
                return response.get(result_key)
            else:
                raise Exception(response.get('errmsg'))

    @classmethod
    def wecom_appchat(cls, msg={}):
        '''向群聊会话发送企业微信通知

        Keyword Arguments:
            msg {dict} -- [推送的企业微信消息] (default: {})
        '''
        url = cls.__url + 'cgi-bin/appchat/send?access_token={}'.format(
            cls.token())
        msg_meta = {
            "chatid": cls.__chatid,
            "msgtype": cls.__msgtype
        }
        msg = dict(msg_meta, **msg)
        data = json.dumps(msg, ensure_ascii=False).encode('utf-8')
        response = requests.post(url=url, data=data)
        return response.json()

    @classmethod
    def wecom_message(cls, msg={}):
        '''向个人会话发送企业微信通知

        Keyword Arguments:
            msg {dict} -- [向企业微信API推送的消息] (default: {})
        '''
        url = cls.__url + 'cgi-bin/message/send?access_token={}'.format(
            cls.token())
        msg_meta = {
            # "touser": touser,
            "agentid": cls.__agentid,
            "msgtype": cls.__msgtype
        }

        msg = dict(msg_meta, **msg)
        data = json.dumps(msg, ensure_ascii=False).encode('utf-8')
        response = requests.post(url=url, data=data)
        return response.json()

    @classmethod
    def send_appchat_hxmis(cls, msg={}):
        '''向蓝鲸封装的企业微信群聊会话接口发送通知
        为了适应初次封装使用了与官方接口不一致的参数

        Keyword Arguments:
            msg {dict} -- [description] (default: {{}})
        '''
        data = {
            "bk_app_code": "bk_nodeman",
            "bk_app_secret": "16944684-7134-4daf-9bd5-a94e0a4b832d",
            "bk_username": "admin",
        }
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        bk_url = "https://paas.hxmis.com/api/c/compapi/bk_ecc_emergency/"
        if cls.__msgtype == "textcard":
            touser = msg.get('touser', [])
            textcard = msg.get('textcard', {})
            if touser:
                data["touser"] = touser
                data["title"] = textcard.get("title", '')
                data["description"] = textcard.get("description", '')
                data["url"] =  textcard.get("url", '')
                data["picurl"] = textcard.get("picurl", '')
                url = bk_url + "send_personal_wechat_message/"
                response = requests.post(url=url, data=json.dumps(
                    data), headers=headers, verify=False)
            else:
                url = bk_url + "send_card_wechat_message/"
                data["title"] = msg['textcard']["title"]
                data["description"] = msg['textcard']["description"]
                data["url"] = msg['textcard']["url"]
                print("send wechat textcard message: " + str(data))
                response = requests.post(url=url, data=data, verify=False)
        elif cls.__msgtype == "text":
            url = bk_url + "send_wechat_message/"
            data["text"] = msg["text"]
            response = requests.post(url=url, data=data, verify=False)
        return response

    @classmethod
    def get_app_list(cls):
        '''获取应用列表
        '''
        url = cls.__url + 'cgi-bin/agent/list?access_token={}'.format(
            cls.token())
        response = requests.get(url=url)
        return response.json()

    @classmethod
    def get_dep_user_list(cls, dep_id, fetch_child=0):
        '''获取指定部门成员

        Arguments:
            dep_id {[type]} -- [部门id]

        Keyword Arguments:
            fetch_child {number} -- [是否获取子部门成员 0不获取 1获取] (default: {0})

        Returns:
            [type] -- [description]
        '''
        url = cls.__url + 'cgi-bin/user/simplelist?access_token={}&department_id={}&fetch_child={}'.format(
            cls.token(), dep_id, fetch_child)
        response = requests.get(url=url)
        return response.json()

    @classmethod
    def create_chart(cls):
        '''创建群聊会话
        '''
        url = cls.__url + 'cgi-bin/appchat/create?access_token={}'.format(
            cls.token())
        data = {
            "name": "Robot - ECC告警监控",
            "owner": "DongFangFang",
            # "userlist": ["DongFangFang", "FeiYe", "WoKeZhenShanLiang", "XingKong"]
            "userlist": ["DongFangFang", "FanQieXiong"]
        }
        data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        response = requests.post(url=url, data=data)
        return response.json()


class Notify(object):
    '''通知类
    '''

    def __init__(self):
        super(Notify, self).__init__()

    @staticmethod
    def get_wecom_msg(group):
        '''调用企业微信消息类型模板插件 生成msg
        Arguments:
            group {[model object]} -- [告警聚合model对象]
        '''
        msgtype = config.WECOM.get('msgtype')
        all_msg = {}
        path = config.WECOM_MSG_TYPE_CLASS.get(msgtype)
        module_path, class_name = path.rsplit('.', maxsplit=1)
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        # print('cls', cls)
        msg = cls(group).msg()
        return {msgtype: msg}

    @classmethod
    def dispatch(cls, group, notify_list, **kwargs):
        ''' 分发通知的类与方法 并执行之
        Arguments:
            group {[model object]} -- [告警聚合对象]
            notify_list {[list]} -- [执行发送通知的方法名]

        Raises:
            Exception -- [description]
        '''
        msg = cls.get_wecom_msg(group)
        touser = '|'.join(kwargs.get('dealer_list', []))
        msg_map = {
            'wecom_appchat': [
                msg
            ],
            'wecom_message': [
                dict({'touser': touser}, **msg)
            ]
        }

        # 根据notify_list发送企业微信通知
        for method in notify_list:
            if DEBUG:
                response = getattr(WeCom, method)(*msg_map.get(method))
            else:
                response = WeCom.send_appchat_hxmis(*msg_map.get(method))
            # print('WeCom.wecom_message response', response)

            # 若企业微信平台返回错误
            if response.get('errcode') != 0:
                raise Exception({'发送通知时企业微信平台返回错误': response})


# if __name__ == '__main__':
    # ret = WeCom._WeCom_token
    # ret = WeCom.token()
    # ret = WeCom.send()
    # ret = WeCom.get_app_list()
    # ret = WeCom.get_dep_user_list(2)
    # ret = WeCom.create_chart()
    # ret = WeCom._WeCom__url
    # print('ret', ret)
