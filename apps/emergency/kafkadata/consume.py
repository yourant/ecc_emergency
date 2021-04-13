from datetime import datetime
from threading import Thread

from kafka import KafkaConsumer

from apps.emergency.kafkadata.utils import into_database
from blueapps.utils.logger import logger
from config import KAFKA


def consume_omnibus_overtime():
    try:
        topics = KAFKA.get('topics')
        broker_list = KAFKA.get('broker_list')
        consumer = KafkaConsumer(
            bootstrap_servers=broker_list,
            group_id='api_data_subscribe_omnibus_overtime',
            # consumer_timeout_ms=20000,
        )
        for topic in topics:
            partitions = consumer.partitions_for_topic(topic)
            logger.info('主题%s对应分区为%s' % (topic, partitions))
        consumer.subscribe(topics=topics)
        for record in consumer:
            # logger.info(datetime.now(), record.topic, record.partition, record.offset)
            into_database(record)
    except Exception as err:
        logger.info(str(err))


thd = Thread(target=consume_omnibus_overtime)
thd.start()
