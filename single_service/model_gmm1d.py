import argparse
import uuid
import matplotlib.pyplot as plt
import numpy as np
from sklearn.utils import check_array
from sklearn.mixture import GaussianMixture
from sklearn.utils.validation import check_is_fitted
from datetime import datetime, timedelta
import os
from io import BytesIO

from database import minio_client
from config import DATA_SERVICE_URL, BUCKET_NAME
from utils import (
    upload_file_to_minio,
    fetch_history_data,
    save_model_to_minio,
    load_model_from_minio,
    save_markdown_to_pdf,
)


class CustomGMM1D:
    def __init__(
        self,
        key="4222126117355524",
        path="油色谱",
        report_path="report.pdf",
        model_path="model.pkl",
        start_time=(datetime.now() - timedelta(days=30)).isoformat(),
        end_time=datetime.now().isoformat(),
        n_components=7,
        contamination=0.01,
    ):
        self.key = key
        self.path = path
        self.report_path = report_path
        self.model_path = model_path
        self.start_time = start_time
        self.end_time = end_time
        self.n_components = n_components
        self.contamination = contamination

        self.detector_ = GaussianMixture(n_components=n_components)
        self.is_all_data_equal = False
        self.all_data_equal_value = None

    def load_data(self) -> np.ndarray:
        """
        Load data from the data service

        Returns:
            np.ndarray: data array of shape (n_samples, 1)
        """
        data = np.array(fetch_history_data(self.key, self.start_time, self.end_time))
        data = data.reshape(-1, 1)
        return data

    def train(self):
        """
        Train the model
        """
        data = self.load_data()
        # check if all data is equal
        if np.all(data == data[0]):
            self.is_all_data_equal = True
            self.all_data_equal_value = data[0][0]

        self.detector_.fit(data)

        scores = self.predict_proba(data)
        self.score_threshold = np.percentile(scores, 100 * self.contamination)

        # find the threshold
        self.threshold_down, self.threshold_up = self.find_min_max_threshold()

        # save the report
        self.generate_report()

        # save the model
        self.save_model()

        return {
            "threshold_down": self.threshold_down,
            "threshold_up": self.threshold_up,
        }

    def predict_proba(self, X):
        if self.is_all_data_equal:
            return np.where(X == np.array([self.all_data_equal_value]), 0, 1)

        check_is_fitted(self.detector_)
        check_array(X)
        return np.exp(self.detector_.score_samples(X))

    def find_min_max_threshold(self):
        # check if the model is fitted
        check_is_fitted(self.detector_)
        train_data = self.load_data()

        if np.all(train_data == train_data[0]):
            return train_data[0][0], train_data[0][0]

        min_value = train_data.min()
        max_value = train_data.max()
        differece = max_value - min_value
        fake_data = np.linspace(
            min_value - differece * 2, max_value + differece * 2, 1000
        )
        result = self.predict_proba(fake_data.reshape(-1, 1))

        first_zero_index = np.where(result >= self.score_threshold)[0][0] - 1
        last_zero_index = np.where(result >= self.score_threshold)[0][-1] + 1
        threshold_down = fake_data[first_zero_index]
        threshold_up = fake_data[last_zero_index]
        print(threshold_down, threshold_up)
        return threshold_down, threshold_up

    def save_model(self):
        """
        Save the model to the minio
        """
        model = {
            "model": self.detector_,
            "threshold_down": self.threshold_down,
            "threshold_up": self.threshold_up,
            "score_threshold": self.score_threshold,
            "is_all_data_equal": self.is_all_data_equal,
            "all_data_equal_value": self.all_data_equal_value,
        }
        save_model_to_minio(BUCKET_NAME, self.model_path, model)

    def load_model(self):
        """
        Load the model from the minio
        """
        model = load_model_from_minio(BUCKET_NAME, self.model_path)
        print(model)
        self.detector_ = model["model"]
        self.threshold_down = model["threshold_down"]
        self.threshold_up = model["threshold_up"]
        self.is_all_data_equal = model["is_all_data_equal"]
        self.all_data_equal_value = model["all_data_equal_value"]
        self.score_threshold = model["score_threshold"]

    def generate_report(self):
        """
        Generate a report for the model
        """
        tmp_file_dir = f"/tmp/{uuid.uuid4()}"
        # tmp_file_dir = "/tmp/test"
        os.makedirs(tmp_file_dir, exist_ok=True)

        check_is_fitted(self.detector_)
        train_data = self.load_data()
        min_value = train_data.min()
        max_value = train_data.max()
        differece = max_value - min_value
        fake_data = np.linspace(
            min_value - differece * 0.8, max_value + differece * 0.8, 1000
        )

        # train data image
        image_buffer = BytesIO()
        train_data_image_path = f"{tmp_file_dir}/train_data.png"
        plt.figure()
        plt.plot(
            train_data.reshape(-1, 1),
            "o",
            label="Train Data",
        )
        plt.title("Train Data")
        plt.savefig(train_data_image_path, format="png", dpi=300)
        plt.close()

        # probility density image
        plt.figure()
        probility_density_image_path = f"{tmp_file_dir}/probility_density.png"
        plt.plot(
            train_data.reshape(-1, 1),
            np.zeros_like(train_data).reshape(-1, 1),
            "o",
            label="Train Data",
        )
        probility = self.predict_proba(fake_data.reshape(-1, 1))
        plt.plot(fake_data, probility, label="Probability Density")
        plt.axhline(self.score_threshold, color="r", linestyle="--")
        plt.axvline(self.threshold_down, color="g", linestyle="--")
        plt.axvline(self.threshold_up, color="g", linestyle="--")
        plt.title("Train Data with Probability Density")
        plt.savefig(probility_density_image_path, format="png", dpi=300)

        text = f"""
# {self.path} 单测点检测模型报告

### 模型详情

测点ID: {self.key}

测点名称: {self.path}

训练数据起始时间: {self.start_time}

训练数据结束时间: {self.end_time}

组件数: {self.n_components}

异常值比例: {self.contamination}

阈值下界: {self.threshold_down}

阈值上界: {self.threshold_up}

### 训练数据分布
![Train Data]({train_data_image_path})

### 概率密度分布
![Probability Density]({probility_density_image_path})
        """

        print(text)

        save_markdown_to_pdf(text=text, save_path=f"{tmp_file_dir}/model_report.pdf")

        upload_file_to_minio(
            BUCKET_NAME, self.report_path, f"{tmp_file_dir}/model_report.pdf"
        )

    def predict(self, value) -> dict:
        """
        Predict the value
        """
        try:
            self.load_model()
        except Exception as e:
            raise Exception(f"Model not trained yet, {e}")

        if self.is_all_data_equal:
            return {
                "status": 0,
                "value": float(value),
                "message": f"{self.path} <b>数据正常</b>",
            }
        value = np.array(value).reshape(-1, 1)

        check_is_fitted(self.detector_)
        # check_is_fitted(self, ["X", "detector_", "threshold_"])
        probs = self.predict_proba(value)
        if probs[0] < self.score_threshold:
            status = 1
        else:
            status = 0
        if status != 0:
            if value < self.threshold_down:
                message = f"{self.path} <b>数据值过小</b>"
            elif value > self.threshold_up:
                message = f"{self.path} <b>数据值过大</b>"
            else:
                message = f"{self.path} <b>数据可能异常</b>"
        else:
            message = f"{self.path} <b>数据正常</b>"

        result = {
            "status": int(status),
            "value": float(value),
            "message": message,
            "threshold_down": self.threshold_down,
            "threshold_up": self.threshold_up,
        }
        return result


if __name__ == "__main__":
    model = CustomGMM1D()
    model.train()
    result = model.predict(0.001)
    print(result)
