import json
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from kafka import KafkaProducer
import config
from utils import get_key_info_by_keywords, fetch_realtime_data, merge_data 

producer = KafkaProducer(
    bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
)


def ingest_main_bearing():
    key_info = get_key_info_by_keywords(["主轴承"])
    keys = [i["key"] for i in key_info]

    data = fetch_realtime_data(keys)

    data = merge_data(key_info, data, key="key")

    # send data to kafka
    for i in data:
        producer.send(config.KAFKA_REALDATA_TOPIC, i)

    producer.flush()
    print("主轴承数据推送成功！")

def ingest_generator():
    key_info = get_key_info_by_keywords(["发电机"])
    keys = [i["key"] for i in key_info]

    data = fetch_realtime_data(keys)

    data = merge_data(key_info, data, key="key")

    # send data to kafka
    for i in data:
        producer.send(config.KAFKA_REALDATA_TOPIC, i)

    producer.flush()
    print("发电机数据推送成功！")

def ingest_gearbox():
    key_info = get_key_info_by_keywords(["齿轮箱"])
    keys = [i["key"] for i in key_info]

    data = fetch_realtime_data(keys)

    data = merge_data(key_info, data, key="key")

    # send data to kafka
    for i in data:
        producer.send(config.KAFKA_REALDATA_TOPIC, i)

    producer.flush()
    print("齿轮箱数据推送成功！")

def ingest_transducer():
    key_info = get_key_info_by_keywords(["变频器"])
    keys = [i["key"] for i in key_info]

    data = fetch_realtime_data(keys)

    data = merge_data(key_info, data, key="key")

    # send data to kafka
    for i in data:
        producer.send(config.KAFKA_REALDATA_TOPIC, i)

    producer.flush()
    print("变频器数据推送成功！")

def ingest_yaw():
    key_info = get_key_info_by_keywords(["偏航"])
    keys = [i["key"] for i in key_info]

    data = fetch_realtime_data(keys)

    data = merge_data(key_info, data, key="key")

    # send data to kafka
    for i in data:
        producer.send(config.KAFKA_REALDATA_TOPIC, i)

    producer.flush()
    print("偏航系统数据推送成功！")

def ingest_default():
    key_info = get_key_info_by_keywords(["监控默认变量"])
    keys = [i["key"] for i in key_info]

    data = fetch_realtime_data(keys)

    data = merge_data(key_info, data, key="key")

    # send data to kafka
    for i in data:
        producer.send(config.KAFKA_REALDATA_TOPIC, i)

    producer.flush()
    print("监控默认变量数据推送成功！")

ingest_main_bearing()
ingest_generator()
ingest_gearbox()
ingest_transducer()
ingest_yaw()
ingest_default()

scheduler = BlockingScheduler()

scheduler.add_job(ingest_main_bearing, IntervalTrigger(minutes=5))
scheduler.add_job(ingest_generator, IntervalTrigger(minutes=5))
scheduler.add_job(ingest_gearbox, IntervalTrigger(minutes=5))
scheduler.add_job(ingest_transducer, IntervalTrigger(minutes=5))
scheduler.add_job(ingest_yaw, IntervalTrigger(minutes=5))
scheduler.add_job(ingest_default, IntervalTrigger(minutes=5))

scheduler.start()
