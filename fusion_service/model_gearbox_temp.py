import argparse
import uuid
from config import BUCKET_NAME
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from numpy.core.numerictypes import ScalarType
from datetime import datetime, timedelta
import os
from typing import Optional
from minio import Minio
from pprint import pprint
import markdown
from weasyprint import HTML, CSS

from utils import (
    fetch_measure_detail,
    fetch_measure_info_by_keyword,
    save_markdown_to_pdf,
    upload_file_to_minio,
    fetch_latest_history_data,
)


class GearboxTempModel:
    def __init__(
        self,
        path="/画笔山风电场/齿轮箱温度/#1号机组",
        device="#1号机组",
        alarm_report_path="alarm_report.pdf",
    ):
        self.path = path
        self.device = device
        self.alarm_report_path = alarm_report_path

        self.data = {}

    def predict(self) -> dict:
        self.message = ""
        self.status = 0

        temp_threshold = 20
        increase_threshold = 2
        data_limit = 10

        diagonosis_measure_info = [
            {
                "name": "齿轮箱油温(max)",
                "temp_threshold": 25,
                "increase_threshold_in_5_minutes": 2,
                "threshold_diff_with_engine_room_temp": 5,
            },
            {
                "name": "齿轮箱入口温度(max)",
                "temp_threshold": 25,
                "increase_threshold_in_5_minutes": 2,
                "threshold_diff_with_engine_room_temp": 5,
            },
            {
                "name": "齿轮箱低速轴承端温度(max)",
                "temp_threshold": 25,
                "increase_threshold_in_5_minutes": 2,
                "threshold_diff_with_engine_room_temp": 5,
            },
            {
                "name": "齿轮箱高速轴承端温度(max)",
                "temp_threshold": 25,
                "increase_threshold_in_5_minutes": 2,
                "threshold_diff_with_engine_room_temp": 5,
            },
        ]

        for measure_info in diagonosis_measure_info:
            measure_name = measure_info["name"]
            temp_threshold = measure_info["temp_threshold"]
            increase_threshold = measure_info["increase_threshold_in_5_minutes"]

            # 机舱温度(avg)
            engine_room_temp_measure_info = fetch_measure_info_by_keyword(
                include=f"{self.device}&机舱温度(avg)"
            )
            engine_room_temp_key = engine_room_temp_measure_info["key"]
            engine_room_temp_measurement_json = fetch_latest_history_data(
                engine_room_temp_measure_info["key"], limit=data_limit
            )
            self.data[f"{engine_room_temp_measure_info['key']}"] = (
                engine_room_temp_measurement_json
            )
            current_engine_room_temp = engine_room_temp_measurement_json[0]["value"]

            measure_info = fetch_measure_info_by_keyword(
                include=f"{self.device}&{measure_name}"
            )
            measure_key = measure_info["key"]
            measure_measurement_json = fetch_latest_history_data(
                measure_info["key"], limit=data_limit
            )
            self.data[f"{measure_info['key']}"] = measure_measurement_json

            # 1. 检查发电机温度是否超过阈值
            if measure_measurement_json[0]["value"] > temp_threshold:
                self.status += 1
                self.message += f"<b>{measure_name}</b>（测点：{measure_key}，实时值：{measure_measurement_json[0]['value']}）超过{temp_threshold}，请注意！\n"

            # 2. 检查发电机温度是否在过去5分钟内上升
            measure_increase_in_last_5_minutes = (
                measure_measurement_json[0]["value"]
                - measure_measurement_json[1]["value"]
            )
            if measure_increase_in_last_5_minutes > increase_threshold:
                self.status += 1
                self.message += f"<b>{measure_name}</b>（测点：{measure_key}）在过去5分钟内上升了{measure_increase_in_last_5_minutes}，请注意！\n"

            # 3. 检查发电机温度与机舱温度的差值
            diff_with_engine_room_temp = (
                measure_measurement_json[0]["value"] - current_engine_room_temp
            )
            if (
                diff_with_engine_room_temp
                > measure_info["threshold_diff_with_engine_room_temp"]
            ):
                self.status += 1
                self.message += f"<b>{measure_name}</b>（测点：{measure_key}）与机舱温度差值为{diff_with_engine_room_temp}，请注意！\n"

        if self.status == 0:
            self.message = "发电机温度正常"
        else:
            # self.status = 3
            self.message = "<b>发电机温度异常</b>\n" + self.message

        # 3. 生成报告
        if self.status > 0:
            self.generate_alarm_report()

        # 4. 返回结果
        return {
            "status": self.status,
            "message": self.message,
        }

    def generate_alarm_report(self):
        # tmp_file_dir = "/tmp/test"
        print("generate report")
        tmp_file_dir = f"/tmp/{uuid.uuid4()}"
        os.makedirs(tmp_file_dir, exist_ok=True)

        # convert to DataFrame
        df_list = []
        for key, value in self.data.items():
            # measure detai
            detail = fetch_measure_detail(key)
            key = detail["name"].split(".")[-1]

            df = pd.DataFrame(value)
            df = df[["time", "value"]]
            # save fresh_time only to minute
            df["time"] = df["time"].apply(lambda x: x[: x.rfind(":")])
            df.columns = ["时间", key]
            df.set_index("时间", inplace=True)
            # remove duplicated time row
            df = df[~df.index.duplicated(keep="first")]

            df_list.append(df)

        # merge all data
        self.data_df = pd.concat(df_list, axis=1)

        data_markdown = self.data_df.to_markdown()

        text = f"""
# {self.path}诊断报告

## 乙炔和氢气监测数据
{data_markdown}

## 诊断信息

{self.message}
        """

        save_markdown_to_pdf(text, f"{tmp_file_dir}/report.pdf")

        upload_file_to_minio(
            BUCKET_NAME, self.alarm_report_path, f"{tmp_file_dir}/report.pdf"
        )


if __name__ == "__main__":
    model = GearboxTempModel()
    result = model.predict()
    model.generate_alarm_report()
    print(result)
    print("Done")
