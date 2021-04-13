import base64
import hashlib
import json
import os
import queue
import sys
import threading
import zlib

from kafka import KafkaConsumer, TopicPartition

from apps.emergency.models import choices, EmergencyOmnibus, EmergencyOvertime, EmergencyOmnibusGroup, EmergencyOvertimeGroup
from apps.lens import lens
from blueapps.utils.logger import logger
from config import KAFKA


class ThreadSafeQueue:

    def __init__(self, capacity=-1):
        self.__capacity = capacity  # 初始化队列大小
        self.__mutex = threading.Lock()  # 初始化互斥量
        self.__cond = threading.Condition(self.__mutex)  # 初始化条件变量
        self.__queue = queue.Queue()  # 初始化队列

    def get(self):

        if self.__cond.acquire():  # 获取互斥锁和条件变量，python中threading条件变量默认包含互斥量，因此只需要获取条件变量即可
            while self.__queue.empty():
                self.__cond.wait()  # 条件变量等待

            elem = self.__queue.get()

            self.__cond.notify()
            self.__cond.release()

        return elem

    def put(self, elem):

        if self.__cond.acquire():
            while self.__queue.qsize() >= self.__capacity:
                self.__cond.wait()
            self.__queue.put(elem)

            self.__cond.notify()
            self.__cond.release()

    def clear(self):

        if self.__cond.acquire():
            self.__queue.queue.clear()

            self.__cond.release()
            self.__cond.notifyAll()

    def empty(self):

        is_empty = False
        if self.__mutex.acquire():  # 只需要获取互斥量
            is_empty = self.__queue.empty()
            self.__mutex.release()

        return is_empty

    def size(self):
        size = 0
        if self.__mutex.acquire():
            size = self.__queue.qsize()
            self.__mutex.release()

        return size

    def resize(self, capacity=-1):
        self.__capacity = capacity


def consume_topic(topic):
    broker_list = KAFKA.get('broker_list')
    consumer = KafkaConsumer(
        bootstrap_servers=broker_list,
        group_id='api_data_topic_poll',
        consumer_timeout_ms=20000,
    )
    partitions = consumer.partitions_for_topic(topic)
    logger.info('主题%s对应分区为%s' % (topic, partitions))
    for partition in partitions:
        tp = TopicPartition(topic, partition)
        consumer.assign([tp])
        logger.info(consumer.end_offsets([tp]))
        # next_offset = consumer.end_offsets([tp_fault]).get(tp_fault)
        # consumer.seek(tp_fault, int(next_offset) - 1)
        msg = consumer.poll(timeout_ms=50)
        if not msg:
            logger.info(str(msg))
        else:
            records = msg.get(tp)
            for record in records:
                into_database(record)
        consumer.commit()


def into_database(record):
    # logger.info(record)
    data = zlib.decompress(base64.b64decode(record.value)).decode('gbk')
    if not os.getenv('BK_ENV'):  # 开发环境判断
        data = eval(data)
    else:
        data = json.loads(data)
    # logger.info(len(data))
    for item in data:
        if not item.get('children'):
            hash_id = hashlib.md5(str(item).encode(encoding='UTF-8')).hexdigest()
            params = {'hash_id': hash_id}
            if item.get('summary'):
                # logger.info('***omnibus***', str(item))
                model_obj = lens._registry.get(EmergencyOmnibus)
                response = model_obj._api(method='GET', data=params)
                if response['code'] == 1:
                    response_data = response.get('data')
                    if not response_data.get('items'):
                        for key, value in item.items():
                            if key in EmergencyOmnibus._meta.field_map.keys():
                                params[EmergencyOmnibus._meta.field_map.get(key)] = value
                            else:
                                params[key] = value
                        params['operation'] = int([choice[0] for choice in choices.get('EmergencyOmnibus_opration') if
                                                   choice[1] == params['operation']][0])
                        params['level'] = '0' if params['level'] not in {'10', '20', '40', '50'} else params['level']
                        # logger.info('omnibus params', params)
                        response = model_obj._api(method='POST', data=params)
                        if response['code'] != 1:
                            logger.info(f'综合类记录{record.topic, record.partition, record.offset}写入失败', str(response))
                    elif response_data.get('items')[0].get('hash_id') == hash_id:
                        logger.info(f'综合类记录{hash_id}已存在{record.topic, record.partition, record.offset}')
                else:
                    logger.info(str(response))
            if item.get('key'):
                model_obj = lens._registry.get(EmergencyOvertime)
                response = model_obj._api(method='GET', data=params)
                if response['code'] == 1:
                    response_data = response.get('data')
                    if not response_data.get('items'):
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
                        # logger.info('overtime params', params)
                        response = model_obj._api(method='POST', data=params)
                        if response['code'] != 1:
                            logger.info(f'交易类记录{record.topic, record.partition, record.offset}写入失败', str(response))
                    elif response_data.get('items')[0].get('hash_id') == hash_id:
                        logger.info(f'交易类记录{hash_id}已存在{record.topic, record.partition, record.offset}')
                else:
                    logger.info(str(response))


