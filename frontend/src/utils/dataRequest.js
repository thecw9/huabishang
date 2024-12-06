import axios from "axios";
import { ElNotification } from "element-plus";

const service = axios.create({
  baseURL: "/data-api",
  // timeout: 5000,
});

service.interceptors.request.use((config) => {
  return config;
});

service.interceptors.response.use(
  (response) => {
    const res = response.data;
    if (res.code !== 200) {
      ElNotification.error({
        title: "请求错误",
        message: res.message,
      });
      return Promise.reject(new Error(res.message || "Error"));
    } else {
      return res;
    }
  },
  (error) => {
    ElNotification.error({
      title: "请求错误",
      message: error.response.data.detail || error.message || "请求错误",
    });
    return Promise.reject(error);
  },
);

export default service;
