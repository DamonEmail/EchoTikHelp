import axios from "axios";
import { ElMessage } from "element-plus";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.code === "ERR_NETWORK") {
      ElMessage.error("无法连接到服务器，请确保后端服务已启动");
    } else if (error.response) {
      ElMessage.error(error.response.data?.detail || "请求失败，请稍后重试");
    } else {
      ElMessage.error("请求失败，请稍后重试");
    }
    return Promise.reject(error);
  }
);

export const createTask = async (data) => {
  const response = await api.post("/crawl", data);
  return response.data;
};

export const getTaskStatus = async (taskId) => {
  const response = await api.get(`/status/${taskId}`);
  return response.data;
};

export const deleteTask = async (taskId) => {
  const response = await api.delete(`/tasks/${taskId}`);
  return response.data;
};

export const startAnalyze = async (data) => {
  const response = await api.post("/analyze", data);
  return response.data;
};
