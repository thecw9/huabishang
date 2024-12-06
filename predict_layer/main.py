from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import subprocess
import shlex
from datetime import datetime

from utils import (
    fetch_all_single_measure_model,
    predict_model_single_measure,
    train_single_measure_model,
    fetch_all_expert_model,
    predict_model_expert,
)


def predict_single_measure():
    print("start predict single measure model")
    models = fetch_all_single_measure_model()
    for model in models:
        key = model["key"]
        predict_model_single_measure(key)

def train_single_measure():
    print("start train single measure model")
    models = fetch_all_single_measure_model()
    for model in models:
        key = model["key"]
        train_single_measure_model(key)

scheduler = BlockingScheduler()


predict_single_measure()
scheduler.add_job(
    predict_single_measure,
    IntervalTrigger(minutes=30),
    misfire_grace_time=60,  # 允许任务延迟最多 60 秒后仍然执行
)

# train_single_measure()
scheduler.add_job(
    train_single_measure,
    IntervalTrigger(days=10),
    misfire_grace_time=60*60*2,  # 允许任务延迟最多 2 小时后仍然执行
)


models = fetch_all_expert_model()
for model in models:
    key = model["key"]
    predict_model_expert(key)
    scheduler.add_job(
        predict_model_expert,
        CronTrigger.from_crontab(model["schedule"]),
        args=[key],
        misfire_grace_time=60,  # 允许任务延迟最多 60 秒后仍然执行
    )
    print(f"add expert model {key} predict job success, schedule: {model['schedule']}")


scheduler.start()
