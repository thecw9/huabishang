from fastapi import FastAPI, APIRouter, Depends, HTTPException
import config
from sqlalchemy import (
    select,
    and_,
    or_,
    func,
    column,
    Table,
    update,
    insert,
    union_all,
    delete,
)
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from sqlalchemy import text
from typing import Optional
from pydantic import BaseModel
from database import engine, Base
from models import Measures, create_measures_monthly_table
from utils import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    Base.metadata.reflect(engine)
    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)
app.title = "Data Service API"


@app.get("/ping")
async def ping():
    return {"code": 200, "message": "success"}


class MeasuresSearchParam(BaseModel):
    include: str = "高抗A相&油色谱 | 高抗B相&接地电流"
    exclude: Optional[str] = None
    exclude_no_unit: bool = False


@app.post("/info")
async def get_measures_keys_by_keywords(
    keywords: MeasuresSearchParam,
    db: Session = Depends(get_db),
):
    """Get keys by keywords
    :param keywords: include, exclude
    :return: keys
    """
    include = keywords.include.replace(" ", "").replace("AND", "&").replace("OR", "|")
    exclude = keywords.exclude
    if exclude:
        exclude = exclude.replace(" ", "").replace("AND", "&").replace("OR", "|")
    exclude_no_unit = keywords.exclude_no_unit

    statement = select(Measures)
    if include:
        or_list = []
        for or_keyword in include.split("|"):
            and_list = []
            for and_keyword in or_keyword.split("&"):
                and_list.append(Measures.path.like(f"%{and_keyword}%"))
            or_list.append(and_(*and_list))
        statement = statement.where(or_(*or_list))
    if exclude:
        for keyword in exclude.split("&"):
            statement = statement.where(~Measures.path.like(f"%{keyword}%"))
    if exclude_no_unit:
        statement = statement.where(Measures.unit != "")

    results = db.execute(statement).scalars().all()

    return {
        "code": 200,
        "message": "success",
        "data": results,
    }


class MeasuresInfoQueryParam(BaseModel):
    key: str = "4222125033390086"


@app.post("/info/detail")
async def get_measures_info_by_key(
    data: MeasuresInfoQueryParam,
    db: Session = Depends(get_db),
):
    """Get measures info by key
    :param key: key
    :return: measures info
    """
    key = data.key

    statement = select(Measures).where(Measures.key == key)
    result = db.execute(statement).scalar()

    if not result:
        raise HTTPException(status_code=404, detail=f"measures {key} not found")

    return {
        "code": 200,
        "message": "success",
        "data": result,
    }


class RealtimeDataSearchParam(BaseModel):
    keys: list[str] = ["4222125033390086", "4222125027229703", "4222125027295239"]


@app.post("/realtime")
async def get_realtime_data(keys: RealtimeDataSearchParam, db=Depends(get_db)):
    if not keys.keys:
        raise HTTPException(status_code=400, detail="keys is empty")

    statement = select(Measures).where(Measures.key.in_(keys.keys))
    results = db.execute(statement).scalars().all()
    return {
        "code": 200,
        "message": "success",
        "data": results,
    }


class RealtimeDataStoreParam(BaseModel):
    key: str = "4222125033390086"
    value: float
    fresh_time: Optional[datetime] = None
    time: Optional[datetime] = None
    unit: Optional[str] = None
    name: Optional[str] = None
    path: Optional[str] = None
    quality: Optional[int] = None


@app.post("/realtime/store")
async def store_realtime_data(
    data: list[RealtimeDataStoreParam], db: Session = Depends(get_db)
):
    if not data:
        raise HTTPException(status_code=400, detail="data is empty")

    data_dict = [d.dict(exclude_none=True) for d in data]

    # check if measures exists
    for d in data_dict:
        key = d["key"]
        statement = select(Measures).where(Measures.key == key)
        result = db.execute(statement).scalar()
        if not result:
            db.execute(insert(Measures), d)

    # update measures table
    db.execute(
        update(Measures),
        data_dict,
    )
    db.commit()

    # insert into history table
    year = datetime.now().year
    month = datetime.now().month
    table_name = f"measures_{year}_{month}"
    # check if table exists
    if Base.metadata.tables.get(table_name) is None:
        table = create_measures_monthly_table(table_name)
        table.create(engine)
    else:
        table = Table(table_name, Base.metadata, autoload_with=engine)
        table.create(engine, checkfirst=True)
    try:
        db.execute(insert(table), data_dict)
    except Exception as e:
        print(e)
        db.rollback()
        return {"code": 400, "message": f"Store data failed: {e}"}
    db.commit()

    return {"code": 200, "message": "Store data success"}


class HistoryDataQueryParam(BaseModel):
    key: str = "test"
    start_time: datetime = datetime.now() - timedelta(days=1)
    end_time: datetime = datetime.now()
    page: Optional[int] = None
    size: Optional[int] = None


@app.post("/history")
async def get_sympton_history(
    history_data_query_param: HistoryDataQueryParam, db=Depends(get_db)
):
    # extract query params
    key = history_data_query_param.key
    start_time = history_data_query_param.start_time
    end_time = history_data_query_param.end_time
    page = history_data_query_param.page
    size = history_data_query_param.size

    # get all symptons table
    tables = [
        table
        for table_name, table in Base.metadata.tables.items()
        if table_name.startswith("measures_")
    ]
    if not tables:
        return {"code": 400, "message": "no history data"}

    # query statement
    statement = union_all(
        *[
            select(table).where(
                and_(table.c.key == key, table.c.time.between(start_time, end_time))
            )
            for table in tables
        ]
    ).order_by(column("time").desc())
    if page and size:
        statement = statement.limit(size).offset((page - 1) * size)

    # query
    results = db.execute(statement).fetchall()
    results = [r._asdict() for r in results]

    # get total count
    total_statement = select(func.count()).select_from(statement.alias("t"))
    total = db.execute(total_statement).scalar()

    return {
        "code": 200,
        "message": "success",
        "data": results,
        "total": total,
    }


class HistoryLatestDataSearchParam(BaseModel):
    key: str = "4222125033390086"
    limit: int = 100


@app.post("/history/latest")
async def get_latest_history_data(
    history_latest_data_search_param: HistoryLatestDataSearchParam, db=Depends(get_db)
):
    key = history_latest_data_search_param.key
    limit = history_latest_data_search_param.limit

    # get all symptons table
    tables = [
        table
        for table_name, table in Base.metadata.tables.items()
        if table_name.startswith("measures_")
    ]
    if not tables:
        return {"code": 400, "message": "no history data"}

    # query statement
    statement = (
        union_all(*[select(table).where(table.c.key == key) for table in tables])
        # .order_by(column("fresh_time").desc())
        .order_by(column("time").desc())
        .limit(limit)
    )

    # query
    results = db.execute(statement).fetchall()
    results = [r._asdict() for r in results]

    return {
        "code": 200,
        "message": "success",
        "data": results,
    }


class HistoryDataDeleteParam(BaseModel):
    start_time: datetime = datetime(2099, 1, 1)
    end_time: datetime = datetime(2099, 12, 30)


@app.post("/history/delete")
async def delete_history_data(
    history_data_delete_param: HistoryDataDeleteParam, db=Depends(get_db)
):
    start_time = history_data_delete_param.start_time
    end_time = history_data_delete_param.end_time

    # get all symptons table
    tables = [
        table
        for table_name, table in Base.metadata.tables.items()
        if table_name.startswith("measures_")
    ]
    if not tables:
        return {"code": 400, "message": "no history data"}

    # delete statement
    for table in tables:
        db.execute(
            delete(table)
            .where(table.c.time >= start_time)
            .where(table.c.time <= end_time)
        )
    db.commit()

    return {
        "code": 200,
        "message": "success",
        "data": f"delete data between {start_time} and {end_time}",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
