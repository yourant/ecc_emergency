import base64
import json
import os
import zlib
from datetime import timedelta

from celery.schedules import crontab
from celery.task import periodic_task
from kafka import KafkaConsumer, TopicPartition

from apps.emergency.kafkadata.models import FaultLocation
from apps.emergency.kafkadata.utils import into_database
from blueapps.utils.logger import logger
from config import KAFKA


@periodic_task(run_every=timedelta(seconds=10))
def consume_omnibus_overtime():
    try:
        topics = KAFKA.get('topics')
        broker_list = KAFKA.get('broker_list')
        consumer = KafkaConsumer(
            bootstrap_servers=broker_list,
            group_id='celery_topic_poll',
            consumer_timeout_ms=20000,
        )
        for topic in topics:
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
    except Exception as err:
        logger.info(str(err))


@periodic_task(run_every=crontab('*/10'))
def consume_fault_location():
    try:
        topic = 'HXB_Fault_Location'
        broker_list = KAFKA.get('broker_list')
        consumer = KafkaConsumer(
            bootstrap_servers=broker_list,
            group_id='celery_fault_location_poll',
            consumer_timeout_ms=20000,
        )
        partitions = consumer.partitions_for_topic(topic)
        logger.info('主题%s对应分区为%s' % (topic, partitions))
        for partition in partitions:
            tp_fault = TopicPartition(topic, partition)
            consumer.assign([tp_fault])
            logger.info(consumer.end_offsets([tp_fault]))
            # next_offset = consumer.end_offsets([tp_fault]).get(tp_fault)
            # consumer.seek(tp_fault, int(next_offset) - 1)
            msg = consumer.poll(timeout_ms=50)
            if not msg:
                logger.info(str(msg))
            else:
                records = msg.get(tp_fault)
                for record in records:
                    logger.info(f'当前记录{record.topic, record.partition, record.offset}')
                    if not os.getenv('BK_ENV'):
                        data = eval(zlib.decompress(base64.b64decode(record.value)).decode('gbk'))
                    else:
                        data = json.loads(record.value.decode('utf-8'))
                    fault_location = FaultLocation.objects.filter(topic=record.topic, partition=int(record.partition), offset=int(record.offset))
                    if fault_location:
                        fault_location[0].offset = int(record.offset)
                        fault_location[0].value = str(data)
                        fault_location[0].save()
                    else:
                        new_fault = FaultLocation(topic=record.topic, partition=int(record.partition), offset=int(record.offset), value=str(data))
                        new_fault.save()
            consumer.commit()
    except Exception as err:
        logger.info(str(err))
