import axios from "@/utils/dataRequest";

export function getMeasuresInfo(
  include,
  exclude = null,
  exclude_no_unit = false,
) {
  const params = {
    include: include,
    exclude: exclude,
    exclude_no_unit: exclude_no_unit,
  };

  return axios.post("/info", params, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
}

export function getMeasuresInfoByKey(key) {
  return axios.post(
    "/info/detail",
    {
      key: key,
    },
    {
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    },
  );
}

export function getDataByKeys(keys) {
  return axios.post(
    "/realtime",
    {
      keys: keys,
    },
    {
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    },
  );
}

// 通过时间获取历史数据
export function getHistoryDataByTime(
  key,
  startTime = null,
  endTime = null,
  page = null,
  size = null,
) {
  const data = {
    key: key,
    start_time: startTime,
    end_time: endTime,
    page: page,
    size: size,
  };
  return axios.post("/history", data, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
}

// 获取最新n条历史数据
export function getLatestHistoryData(key, limit) {
  return axios.post(
    "/history/latest",
    {
      key: key,
      limit: limit,
    },
    {
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    },
  );
}

async function getKeysData(include, exclude) {
  const res = await getMeasuresInfo(include, exclude);
  const keys = res.data.map((item) => {
    return item.key;
  });
  return keys;
}

export async function getDataByKeywords(include, exclude) {
  const keys = await getKeysData(include, exclude);
  const res = await getDataByKeys(keys);
  return res;
}
