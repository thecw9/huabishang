import axios from "@/utils/singleModelRequest";

export function trainSingleModel(key, startTime, endTime) {
  const data = {
    key: key,
    start_time: startTime,
    end_time: endTime,
  };
  return axios.post("/model/train", data, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
}

export function getSingleModelInfo(include, exclude = null) {
  const params = {
    include: include,
    exclude: exclude,
  };

  return axios.post("/model/info", params, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
}

export function getSingleModelDetailByKey(key) {
  const params = {
    key: key,
  };

  return axios.post("/model/detail", params, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
}

export function getSingleModelAlarmInfo(
  include,
  exclude = null,
  startTime = null,
  endTime = null,
  page = null,
  pageSize = null,
) {
  const params = {
    include: include,
    exclude: exclude,
    start_time: startTime,
    end_time: endTime,
    page: page,
    size: pageSize,
  };

  return axios.post("/alarm", params, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
}
