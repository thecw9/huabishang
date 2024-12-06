from fastapi import FastAPI, Body
import traceback
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from model_gmm1d import CustomGMM1D
from contextlib import asynccontextmanager
from database import db
from utils import fetch_realtime_data, fetch_measure_detail

alarm_collection = db["alarm"]
model_info_collection = db["models"]

app = FastAPI()
app.title = "Singel Measure Model API"


class TrainModelParams(BaseModel):
    key: str = "4222126793687042"
    start_time: datetime = datetime.now() - timedelta(days=1)
    end_time: datetime = datetime.now()


@app.post("/model/train")
async def train_gmm1d(params: TrainModelParams):
    measure_detail = fetch_measure_detail(params.key)

    model_info_db = model_info_collection.find_one({"key": params.key})
    if model_info_db:
        # update model info
        model_info_collection.update_one(
            {"key": params.key},
            {
                "$set": {
                    "start_time": params.start_time,
                    "end_time": params.end_time,
                }
            },
        )
        model_info_db["start_time"] = params.start_time
        model_info_db["end_time"] = params.end_time
        model_info = model_info_db
    else:
        # insert model info
        model_info = {}
        model_info["key"] = params.key
        model_info["path"] = measure_detail["path"]
        model_info["model_type"] = "gmm1d"
        model_info["report_path"] = f"report/gmm1d/{params.key}.pdf"
        model_info["model_path"] = f"model/gmm1d/{params.key}.pkl"
        model_info["start_time"] = params.start_time.isoformat()
        model_info["end_time"] = params.end_time.isoformat()
        model_info["n_components"] = 5
        model_info["contamination"] = 0.01
        model_info_collection.insert_one(model_info)

    model = CustomGMM1D(
        key=model_info["key"],
        path=model_info["path"],
        report_path=model_info["report_path"],
        model_path=model_info["model_path"],
        start_time=model_info["start_time"],
        end_time=model_info["end_time"],
        n_components=model_info["n_components"],
        contamination=model_info["contamination"],
    )

    try:
        result = model.train()
    except Exception as e:
        # drop model info
        model_info_collection.delete_one({"key": params.key})
        return {"code": 500, "message": traceback.format_exc()}

    model_info["threshold_down"] = result["threshold_down"]
    model_info["threshold_up"] = result["threshold_up"]
    # update model_info_collection
    model_info_collection.update_one(
        {"key": params.key},
        {
            "$set": {
                "train_time": datetime.now().isoformat(),
                "threshold_down": result["threshold_down"],
                "threshold_up": result["threshold_up"],
                "status": 0,
                "message": "",
            }
        },
    )

    return {"code": 200, "message": "模型训练成功"}


class ModelQueryParam(BaseModel):
    include: str = "韶山站&声音&通道1 | 韶山站&声音&通道2"
    exclude: Optional[str] = None


@app.post("/model/info")
async def get_model_info(model_query_param: ModelQueryParam = Body(...)):
    include = model_query_param.include
    exclude = model_query_param.exclude
    include = (
        model_query_param.include.replace(" ", "")
        .replace("AND", "&")
        .replace("OR", "|")
    )
    exclude = model_query_param.exclude
    if exclude:
        exclude = exclude.replace(" ", "").replace("AND", "&").replace("OR", "|")

    query = {}
    if include:
        or_items = []
        for item in include.split("|"):
            and_items = []
            for sub_item in item.split("&"):
                and_items.append({"path": {"$regex": sub_item}})
            or_items.append({"$and": and_items})
        query["$or"] = or_items
    if exclude:
        and_items = []
        for item in exclude.split("&"):
            and_items.append({"path": {"$not": {"$regex": item}}})
        query["$and"] = and_items

    model_info = model_info_collection.find(query)
    model_info = [{**item, "_id": str(item["_id"])} for item in model_info]
    return {
        "code": 200,
        "msg": "success",
        "data": list(model_info),
    }


class ModelDetailParam(BaseModel):
    key: str


@app.post("/model/detail")
async def get_model_detail(params: ModelDetailParam):
    model_info = model_info_collection.find_one({"key": params.key})
    if not model_info:
        return {"code": 404, "message": "模型不存在"}
    model_info["_id"] = str(model_info["_id"])
    return {"code": 200, "message": "获取模型信息成功", "data": model_info}


class ModelPredictParams(BaseModel):
    key: str


# predict
@app.post("/model/predict")
async def predict_gmm1d(params: ModelPredictParams):
    model_info = model_info_collection.find_one({"key": params.key})
    if not model_info:
        return {"code": 404, "message": "模型不存在"}
    model = CustomGMM1D(
        key=model_info["key"],
        path=model_info["path"],
        report_path=model_info["report_path"],
        model_path=model_info["model_path"],
        start_time=model_info["start_time"],
        end_time=model_info["end_time"],
        n_components=model_info["n_components"],
        contamination=model_info["contamination"],
    )
    real_time_data = fetch_realtime_data(params.key)
    result = model.predict(real_time_data["value"])

    # update model_info_collection
    model_info_collection.update_one(
        {"key": params.key},
        {
            "$set": {
                "fresh_time": real_time_data["fresh_time"],
                "service_time": real_time_data["service_time"],
                "predict_time": datetime.now().isoformat(),
                "value": real_time_data["value"],
                "status": result["status"],
                "message": result["message"],
                "result": result,
            }
        },
    )

    # save to predict collection
    if result["status"] != 0:
        predict_result = {
            "key": params.key,
            "path": model_info["path"],
            "fresh_time": real_time_data["fresh_time"],
            "predict_time": datetime.now().isoformat(),
            "value": real_time_data["value"],
            "status": result["status"],
            "message": result["message"],
            "result": result,
        }
        alarm_collection.insert_one(predict_result)

    return {"code": 200, "message": "预测成功", "data": result}


class AlarmQueryParam(BaseModel):
    include: str = "潇湘站&油色谱 | 潇湘站&高抗B相"
    exclude: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    page: Optional[int] = 1
    size: Optional[int] = 10


@app.post("/alarm")
async def get_alarm_info(alarm_query_param: AlarmQueryParam = Body(...)):
    include = alarm_query_param.include
    exclude = alarm_query_param.exclude
    start_time = alarm_query_param.start_time
    end_time = alarm_query_param.end_time
    page = alarm_query_param.page
    size = alarm_query_param.size
    include = (
        alarm_query_param.include.replace(" ", "")
        .replace("AND", "&")
        .replace("OR", "|")
    )
    exclude = alarm_query_param.exclude
    if exclude:
        exclude = exclude.replace(" ", "").replace("AND", "&").replace("OR", "|")

    query = {}
    if include:
        or_items = []
        for item in include.split("|"):
            and_items = []
            for sub_item in item.split("&"):
                and_items.append({"path": {"$regex": sub_item}})
            or_items.append({"$and": and_items})
        query["$or"] = or_items
    if exclude:
        and_items = []
        for item in exclude.split("&"):
            and_items.append({"path": {"$not": {"$regex": item}}})
        query["$and"] = and_items

    if start_time and end_time:
        query["predict_time"] = {
            "$gte": start_time.isoformat(),
            "$lte": end_time.isoformat(),
        }

    # total
    total = alarm_collection.count_documents(query)

    if page and size:
        alarm_info = (
            alarm_collection.find(query)
            .sort("predict_time", -1)
            .skip((page - 1) * size)
            .limit(size)
        )
    else:
        alarm_info = alarm_collection.find(query)

    alarm_info = [{**item, "_id": str(item["_id"])} for item in alarm_info]
    return {
        "code": 200,
        "msg": "success",
        "data": list(alarm_info),
        "total": total,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=48011)
