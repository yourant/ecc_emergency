from apps.emergency import models
from apps.lens import lens
from config import QUEUE_EMERGENCYOMNIBUSGROUP, QUEUE_EMERGENCYOVERTIMEGROUP, QUEUE_TEST
from config.dev import DEBUG


class EmergencyMQ(object):
    """向前端WebSocket存放数据的队列中推送数据的工具类"""
    _queue_map = {
        models.EmergencyOmnibusGroup: QUEUE_EMERGENCYOMNIBUSGROUP,
        models.EmergencyOvertimeGroup: QUEUE_EMERGENCYOVERTIMEGROUP
    }

    def __init__(self):
        super(Websocket, self).__init__()

    @classmethod
    def send(cls, model_class, query={}):
        '''向前端的消息队列里放置数据

        [description]

        Arguments:
            model_class {[type]} -- [description]

        Keyword Arguments:
            query {dict} -- [description] (default: {{}})
        '''
        # print('EmergencyMQ.send', model_class)
        model_obj = lens._registry.get(model_class)
        # data = {
        #     # 'status': 1,
        # }
        response = model_obj._api('get', query)
        # print('EmergencyMQ.send response', type(response), response)
        # for x in response.get('data').get('items'):
        #     x['summary'] = '233'

        queue = cls._queue_map.get(model_class)
        queue.put(response)
        if DEBUG:
            QUEUE_TEST.put(response)
