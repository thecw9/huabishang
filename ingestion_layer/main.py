from kafka import KafkaConsumer
import config
import json

from utils import store_realtime_data

# 创建Kafka Consumer
consumer = KafkaConsumer(
    config.KAFKA_REALDATA_TOPIC,
    bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,  # 替换为你的Kafka服务器地址
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

# 消费消息
buffer = []
for message in consumer:
    print(message.value)
    buffer.append(message.value)  # 将消息添加到缓冲区

    if len(buffer) >= 10:
        try:
            store_realtime_data(buffer)  # 调用存储函数
        except Exception as e:
            print("存储失败！", e)
            raise e
        buffer = []  # 清空缓冲区，准备接收下一批消息

    print("存储成功！")
