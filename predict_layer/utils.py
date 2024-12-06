import requests
from datetime import datetime, timedelta
from datetime import datetime
import logging
from pprint import pprint

import config


def fetch_all_single_measure_model():
    url = f"{config.SINGLE_MEASURE_MODEL_URL}/model/info"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = {"include": "", "exclude": ""}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(response.text)
    data = response.json()
    if data["code"] != 200:
        raise Exception(data["message"])
    return data["data"]

def train_single_measure_model(key):
    url = f"{config.SINGLE_MEASURE_MODEL_URL}/model/train"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = {"key": key, "start_time": (datetime.now() - timedelta(days=30)).isoformat(), "end_time": datetime.now().isoformat()}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(response.text)
    data = response.json()
    if data["code"] != 200:
        raise Exception(data["message"])
    return data["message"]


def predict_model_single_measure(key):
    url = f"{config.SINGLE_MEASURE_MODEL_URL}/model/predict"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = {"key": key}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(response.text)
    data = response.json()
    if data["code"] != 200:
        raise Exception(data["message"])
    return data["data"]


def fetch_all_expert_model():
    url = f"{config.EXPERT_MODEL_URL}/model/info"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = {"include": "", "exclude": ""}
    response = requests.post(url, headers=headers, json=data, timeout=10)
    if response.status_code != 200:
        raise Exception(response.text)
    data = response.json()
    if data["code"] != 200:
        raise Exception(data["message"])
    return data["data"]


def predict_model_expert(key):
    print(f"predicting expert model: {key}, time: {datetime.now()}")
    url = f"{config.EXPERT_MODEL_URL}/model/predict"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = {"key": key}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(response.text)
    data = response.json()
    if data["code"] != 200:
        raise Exception(data["message"])
    return data["data"]


if __name__ == "__main__":
    data = fetch_all_single_measure_model()
    pprint(data)

    if len(data) > 0:
        key = data[0]["key"]
        train_single_measure_model(key)
        data = predict_model_single_measure(key)
        print(data)

    models = fetch_all_expert_model()
    print(models)

    key = models[0]["key"]
    data = predict_model_expert(key)
    print(data)
