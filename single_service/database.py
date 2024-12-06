import config
from pymongo import MongoClient
from minio import Minio

client = MongoClient(config.MONGODB_HOST, config.MONGODB_PORT)
db = client["csust_gmm1d"]

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
