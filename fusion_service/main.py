from fastapi import FastAPI, Body
import traceback
import uuid
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from contextlib import asynccontextmanager
from database import model_info_collection, alarm_collection
from utils import fetch_realtime_data, fetch_measure_detail

from init import init
from model_generator_temp import GeneratorTempModel
from model_gearbox_temp import GearboxTempModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    init()
    yield
    pass


app = FastAPI(lifespan=lifespan)
app.title = "Expert Model API"


class ModelQueryParam(BaseModel):
    include: str = "高抗A相"
    exclude: Optional[str] = None
    model_type: Optional[str] = None


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

    if model_query_param.model_type:
        query["model_type"] = model_query_param.model_type

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
    key = params.key
    query = {"key": key}

    model_info = model_info_collection.find(query)
    model_info = [{**item, "_id": str(item["_id"])} for item in model_info]
    return {
        "code": 200,
        "msg": "success",
        "data": list(model_info),
    }


class ModelPredictParams(BaseModel):
    key: str


# predict
@app.post("/model/predict")
async def predict_expert(params: ModelPredictParams):
    model_info = model_info_collection.find_one({"key": params.key})
    alarm_report_path = f"alarm_report/{params.key}/{uuid.uuid4()}.pdf"
    if not model_info:
        return {"code": 404, "message": "模型不存在"}
    model_type = model_info["model_type"]
    if model_type == "generator-temp-model":
        model = GeneratorTempModel(
            path=model_info["path"],
            device=model_info["device"],
            alarm_report_path=alarm_report_path,
        )
    elif model_type == "gearbox-temp-model":
        model = GearboxTempModel(
            path=model_info["path"],
            device=model_info["device"],
            alarm_report_path=alarm_report_path,
        )
    else:
        return {"code": 404, "message": f"模型类型{model_type}不存在"}

    try:
        result = model.predict()
    except Exception as e:
        result = {"status": -1, "message": traceback.format_exc()}

    # update model_info_collection
    model_info_collection.update_one(
        {"key": model_info["key"]},
        {
            "$set": {
                "last_predict_time": datetime.now().isoformat(),
                "status": result["status"],
                "message": result["message"],
                "alarm_report_path": alarm_report_path,
                # "data": result["data"],
            }
        },
    )

    # save to predict collection
    if result["status"] > 0:
        predict_result = {
            "key": model_info["key"],
            "path": model_info["path"],
            "model_type": model_info["model_type"],
            "model_name": model_info["model_name"],
            "alarm_report_path": alarm_report_path,
            "device": model_info["device"],
            "predict_time": datetime.now().isoformat(),
            # "value": result["data"],
            "status": result["status"],
            "message": result["message"],
        }
        alarm_collection.insert_one(predict_result)

    return {"code": 200, "message": "预测成功", "data": result}


class AlarmQueryParam(BaseModel):
    include: str = "韶山站&声音&通道1 | 韶山站&声音&通道2"
    exclude: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    page: Optional[int] = None
    size: Optional[int] = None


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
        alarm_info = alarm_collection.find(query).skip((page - 1) * size).limit(size)
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

    uvicorn.run(app, host="0.0.0.0", port=48012)
