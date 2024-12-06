import os
from pathlib import Path
import numpy as np
import pickle
from typing import Optional
from minio import Minio
import json
from pprint import pprint
import re
from io import BytesIO, StringIO
import shlex
import subprocess
from database import minio_client
import requests
from datetime import datetime, timedelta
import markdown
from weasyprint import HTML, CSS

from config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    BUCKET_NAME,
    DATA_SERVICE_URL,
    SINGLE_MODEL_SERVICE_URL,
    USE_SINGLE_MODEL_THRESHOLD,
)

# MINIO_ENDPOINT = "127.0.0.1:9000"
# MINIO_ACCESS_KEY = "minioadmin"
# MINIO_SECRET_KEY = "minioadmin"
# BUCKET_NAME = "power-prophet"
# DATA_SERVICE_URL = "http://127.0.0.1:8001"


def upload_file_to_minio(bucket_name: str, object_name: str, file_path: str):
    print(
        f"Uploading {file_path} to MinIO bucket {bucket_name} with object name {object_name}"
    )
    # create bucket if not exists
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    # check file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found")

    # set content type
    if Path(file_path).suffix == ".pdf":
        content_type = "application/pdf"
    elif Path(file_path).suffix == ".pkl":
        content_type = "application/pickle"
    else:
        content_type = "application/octet-stream"

    try:
        minio_client.fput_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path,
            content_type=content_type,
        )
    except Exception as e:
        print(e)


def download_and_run_from_minio(bucket_name, object_name, params_command_str: str = ""):
    model_file_bytes = minio_client.get_object(
        bucket_name=bucket_name, object_name=object_name
    )
    model_file_io = StringIO(model_file_bytes.read().decode("utf-8"))
    model_file_io.seek(0)
    model_file_bytes.close()
    model_file_bytes.release_conn()

    command = ["python3", "-c", model_file_io.read()] + shlex.split(params_command_str)

    process = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )
    return process


def check_object_exists(bucket_name: str, object_name: str) -> bool:
    try:
        minio_client.stat_object(bucket_name, object_name)
        return True
    except Exception as e:
        return False


def save_model_to_minio(bucket_name: str, object_name: str, model):
    model_files_io = BytesIO()
    np.save(model_files_io, pickle.dumps(model))
    model_files_io.seek(0)
    minio_client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=model_files_io,
        length=model_files_io.getbuffer().nbytes,
    )
    model_files_io.close()


def load_model_from_minio(bucket_name: str, object_name: str):
    model_bytes = minio_client.get_object(
        bucket_name=bucket_name, object_name=object_name
    )
    model_bytes_downloaded = BytesIO(model_bytes.read())
    model_bytes_downloaded.seek(0)
    model = pickle.loads(np.load(model_bytes_downloaded))

    model_bytes.close()
    model_bytes.release_conn()
    return model


def fetch_all_measures_info():
    url = DATA_SERVICE_URL + "/info"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = {"include": "", "exclude": ""}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        raise Exception(response.text)
    measures = response.json()["data"]
    return measures


def fetch_measure_info_by_keyword(include, exclude=""):
    url = f"{DATA_SERVICE_URL}/info"
    response = requests.post(
        url,
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={
            "include": include,
            "exclude": exclude,
        },
    )
    if response.status_code != 200:
        raise Exception(response.text)

    data = response.json()
    if data["code"] != 200:
        raise Exception(data["message"])

    if len(data["data"]) == 0:
        raise Exception(f"No data found for keyword {include}")

    if len(data["data"]) > 1:
        raise Exception(
            "More than one data found, please specify the more detail keyword"
        )

    return data["data"][0]


def fetch_history_data(key, start_time, end_time):
    if type(start_time) is datetime:
        start_time = start_time.isoformat()
    if type(end_time) is datetime:
        end_time = end_time.isoformat()
    url = f"{DATA_SERVICE_URL}/history"
    response = requests.post(
        url,
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={
            "key": key,
            "start_time": start_time,
            "end_time": end_time,
        },
    )
    if response.status_code != 200:
        raise Exception(response.text)
    data = response.json()
    if data["code"] != 200:
        raise Exception(data["message"])
    # data = [i["value"] for i in data["data"]]
    return data["data"]


def fetch_latest_history_data(key, limit):
    url = f"{DATA_SERVICE_URL}/history/latest"
    response = requests.post(
        url,
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={
            "key": key,
            "limit": limit,
        },
    )
    if response.status_code != 200:
        raise Exception(response.text)
    data = response.json()
    if data["code"] != 200:
        raise Exception(data["message"])
    return data["data"]


def fetch_realtime_data(key: str):
    url = f"{DATA_SERVICE_URL}/realtime"
    response = requests.post(
        url,
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={
            "keys": [key],
        },
    )
    if response.status_code != 200:
        raise Exception(response.text)

    data = response.json()
    if data["code"] != 200:
        raise Exception(data["message"])

    return data["data"][0]


def fetchone_realtime_data_by_keyword(include, exclude=""):
    url = f"{DATA_SERVICE_URL}/info"
    response = requests.post(
        url,
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={
            "include": include,
            "exclude": exclude,
        },
    )
    if response.status_code != 200:
        raise Exception(response.text)

    data = response.json()
    if data["code"] != 200:
        raise Exception(data["message"])

    if len(data["data"]) == 0:
        raise Exception("No data found")

    if len(data["data"]) > 1:
        raise Exception(
            "More than one data found, please specify the more detail keyword"
        )

    return data["data"][0]


def fetch_measure_detail(key):
    url = f"{DATA_SERVICE_URL}/info/detail"
    response = requests.post(
        url,
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={
            "key": key,
        },
    )
    if response.status_code != 200:
        raise Exception(response.text)
    data = response.json()
    if data["code"] != 200:
        raise Exception(data["message"])
    return data["data"]


def save_markdown_to_pdf(text, save_path):
    # 将Markdown转换为HTML
    html_text = markdown.markdown(text, extensions=["tables", "fenced_code"])

    # 将HTML转换为PDF
    HTML(string=html_text).write_pdf(save_path, stylesheets=[CSS(filename="style.css")])


# 判断是否超过单测点模型的阈值
def is_over_single_model_threshold(key: str):
    # NOTE: 当模型不存在或者不使用单测点模型阈值时，返回True
    if not USE_SINGLE_MODEL_THRESHOLD:
        return 0

    url = f"{SINGLE_MODEL_SERVICE_URL}/model/detail"
    response = requests.post(
        url,
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={
            "key": key,
        },
    )
    if response.status_code != 200 or response.json()["code"] != 200:
        return 0
    data = response.json()["data"]
    threshold_down = data["threshold_down"]
    threshold_up = data["threshold_up"]
    realtime_data = fetch_realtime_data(key)
    realtime_value = realtime_data["value"]
    if realtime_value < threshold_down or realtime_value > threshold_up:
        return 1
    else:
        return -1


if __name__ == "__main__":
    object_name = "test.py"

    upload_file_to_minio(
        bucket_name=BUCKET_NAME,
        object_name=object_name,
        file_path="./test_script/test.py",
    )

    process = download_and_run_from_minio(
        bucket_name=BUCKET_NAME,
        object_name=object_name,
        params_command_str="--name 'John Doe'",
    )
    print(process)

    measures = fetch_all_measures_info()
    pprint(measures)

    end_time = datetime.now().isoformat()
    start_time = (datetime.now() - timedelta(days=30)).isoformat()
    history_data = fetch_history_data("4222125033390086", start_time, end_time)
    print("History data:", history_data)

    realtime_data = fetch_realtime_data("4222126793687042")
    print("Realtime data:", realtime_data)

    realtime_data = fetchone_realtime_data_by_keyword("1000kV潇江Ⅰ线高抗A相&乙炔测量量")
    print(realtime_data)

    history_data = fetch_latest_history_data("4222125033390086", 10)
    print("Latest history data:", history_data)

    measure_detail = fetch_measure_detail("4222125033390086")
    # pprint(measure_detail)
