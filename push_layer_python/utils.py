import os
import requests
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import engine

db = Session(engine)
ENVIRONMENT = os.environ["ENVIRONMENT"]


def get_key_info_by_keywords(include: list[str], exclude: list[str] = []) -> list[dict]:
    if include:
        include_conditions = [f"path LIKE '%{i}%'" for i in include]
        where_clause = f"WHERE {' AND '.join(include_conditions)}"
    else:
        where_clause = ""

    if exclude:
        exclude_conditions = [f"path NOT LIKE '%{e}%'" for e in exclude]
        where_clause += (
            f" AND {' AND '.join(exclude_conditions)}"
            if where_clause
            else f"WHERE {' AND '.join(exclude_conditions)}"
        )

    statement = f"""
    SELECT *
    FROM analog
    {where_clause}
    """

    results = db.execute(text(statement)).fetchall()
    results = [r._asdict() for r in results]
    results = [
        {
            "key": i.get("id"),
            "unit": i.get("unitsymbol"),
            "name": i.get("name"),
            "path": i.get("path"),
            "quality": int(i.get("quality") or 0),
        }
        for i in results
    ]
    return results


def fetch_realtime_data_from_api(keys: list[str]):
    url = "http://192.168.4.117/v1/cs/realdata-service/data/realtime"
    headers = {
        "X-HW-ID": "your-hw-id",  # Replace with your actual X-HW-ID
        "X-HW-APPKEY": "your-app-key",  # Replace with your actual X-HW-APPKEY
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ6enciLCJ2ZXIiOiJKV1QxLjAiLCJvYmpfaWQiOm51bGwsImxhc3RfbG9naW4iOjAsInByaSI6W10sInNjb3BlIjpbImFsbCJdLCJpc3MiOiJ4aWFveGlhbmdAbnJlYyIsImV4cCI6MTcwMzU3ODQwODcxNywianRpIjoiOWY1YzMxZjMtYTNmMy00ZmU0LWFmNmMtN2E1ZDBlODVjZjllIiwiYWNjb3VudCI6bnVsbCwiY2xpZW50X2lkIjoienp3In0.gYiNX8IQ0nLP4P8XUl5JwFMFAlsR79EooCjf0MXR0z3ZrGZZ2Ohg8M_VmfkBp0mxTUSlHvJaQIm8ElQY4B7q0PLhHSr5i1Zj0ewLytR6hfsBxn01FqcgxOWgdCF5Tnc7cwa2DZPlIt1E0SIHlJGlKsBHTFfHB5ZmcnDZgaOvEz4",  # Replace with your actual token
    }

    values = []
    for i in range(0, len(keys), 1000):
        keys_chunk = keys[i : i + 1000]
        payload = {
            "id": 1,
            "clientId": "serv-x01",
            "body": {"datatype": "analog", "keys": keys_chunk},
        }
        response = requests.post(url, headers=headers, json=payload, verify=False)
        json_resp = response.json()
        values += json_resp["body"]["values"]
    values = [
        {
            "key": str(v["key"]),
            "value": v["value"],
            "time": v["time_stamp"].replace(" ", "T"),
            "fresh_time": v["fresh_time"].replace(" ", "T"),
        }
        for v in values
    ]
    return values


current_data_index = {}


def fetch_realtime_data_mock(keys: list[str]):
    # all tables start with "scada_analogueother" in the database
    statement = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name LIKE 'scada_analogueother%'
    """
    results = db.execute(text(statement)).fetchall()
    tables = [r[0] for r in results]
    # NOTE: exclude the table "scada_analogueother202310"
    tables = [table for table in tables if table != "scada_analogueother202310"]

    results = []
    for key in keys:
        # count the number of data in all tables
        statement = f"""
        { ' UNION ALL '.join([f"SELECT COUNT(*) FROM {table} WHERE attr_oid = {key}" for table in tables]) }
        """
        result = db.execute(text(statement)).fetchall()
        counts = [r[0] for r in result]
        tables_exist_data = [table for table, count in zip(tables, counts) if count > 0]
        total = sum(counts)

        # get the current data
        global current_data_index
        current_data_index[key] = current_data_index.get(key, 0) + 1
        current_data_index[key] = current_data_index[key] % total
        # current_data_index[key] = current_data_index[key] % (total - 50) + 50

        statement = f"""
        { ' UNION ALL '.join([f"SELECT * FROM {table} WHERE attr_oid = {key}" for table in tables_exist_data]) }
        ORDER BY attr_time
        LIMIT 1 OFFSET {current_data_index[key]}
        """
        result = db.execute(text(statement)).fetchall()
        results.append(result[0]._asdict())

    # time to isoformat
    results = [
        {
            "key": str(i.get("attr_oid")),
            "value": i.get("fvalue"),
            "time": datetime.now().isoformat(),
            # "time": (datetime.now() - timedelta(days=6)).isoformat(),
            "fresh_time": i.get("attr_time").isoformat(),
        }
        for i in results
    ]

    return results

def fetch_realtime_data(keys: list[str]):
    if ENVIRONMENT == "production":
        return fetch_realtime_data_from_api(keys)
    else:
        return fetch_realtime_data_mock(keys)

def merge_data(arr1: list[dict], arr2: list[dict], key: str = "key") -> list[dict]:
    df1 = pd.DataFrame(arr1)
    df2 = pd.DataFrame(arr2)
    df = pd.merge(df1, df2, on=key, how="inner")
    return df.to_dict(orient="records")


if __name__ == "__main__":
    from pprint import pprint

    key_info = get_key_info_by_keywords(["主轴承"])
    pprint(key_info)
    keys = [i["key"] for i in key_info]

    print("Start fetching data...")
    data = fetch_realtime_data(keys)
    pprint(data)

    print("Start merging data...")
    data = merge_data(key_info, data, key="key")
    pprint(data)
