from database import model_info_collection
from utils import upload_file_to_minio
from config import BUCKET_NAME


def init_generator_temp_models():
    models = [
        {
            "key": f"HuaBiShang.GeneratorTempModel.#{i}",
            "path": f"/画笔山风电场/发电机温度模型/#{i}号机组",
            "device": f"#{i}号机组",
            "model_name": "发电机温度模型",
            "model_type": "generator-temp-model",
            "report_path": f"report/画笔山风电场/发电机温度模型/{i}号机组_2021-07-01_2021-07-31.pdf",
        }
        for i in range(1, 14)
    ]
    cron = "2 * * * *"
    for model in models:
        model["schedule"] = cron

    model_info_collection.insert_many(models)
    print("inserted c2h2 h2 models")

    # upload report files to minio
    for model in models:
        upload_file_to_minio(
            bucket_name=BUCKET_NAME,
            object_name=model["report_path"],
            file_path="./assets/特高压换流变油色谱异常处置策略（试行）.pdf",
        )


def init_gearbox_temp_models():
    models = [
        {
            "key": f"HuaBiShang.GearboxTempModel.#{i}",
            "path": f"/画笔山风电场/齿轮箱温度模型/#{i}号机组",
            "device": f"#{i}号机组",
            "model_name": "齿轮箱温度模型",
            "model_type": "gearbox-temp-model",
            "report_path": f"report/画笔山风电场/齿轮箱温度模型/{i}号机组_2021-07-01_2021-07-31.pdf",
        }
        for i in range(1, 14)
    ]
    cron = "2 * * * *"
    for model in models:
        model["schedule"] = cron

    model_info_collection.insert_many(models)
    print("inserted gearbox temp models")

    # upload report files to minio
    for model in models:
        upload_file_to_minio(
            bucket_name=BUCKET_NAME,
            object_name=model["report_path"],
            file_path="./assets/特高压换流变油色谱异常处置策略（试行）.pdf",
        )


def init():
    model_info_collection.drop()
    init_generator_temp_models()
    init_gearbox_temp_models()


if __name__ == "__main__":
    init()
