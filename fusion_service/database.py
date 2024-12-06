from pymongo import MongoClient
from minio import Minio
import redis
import config

client = MongoClient(config.MONGODB_HOST, config.MONGODB_PORT)
db = client["csust_fusion"]

model_info_collection = db["models"]
alarm_collection = db["alarm"]

minio_endpoint = config.MINIO_ENDPOINT
access_key = config.MINIO_ACCESS_KEY
secret_key = config.MINIO_SECRET_KEY
bucket_name = config.BUCKET_NAME
minio_client = Minio(
    minio_endpoint,
    access_key=access_key,
    secret_key=secret_key,
    secure=False,
)

redis_pool = redis.ConnectionPool(host=config.REDIS_HOST, port=config.REDIS_PORT)
