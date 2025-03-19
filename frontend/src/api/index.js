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
  try {
    // 如果没有 taskId，直接获取任务列表
    const url = taskId ? `/status/${taskId}` : "/tasks";
    const response = await api.get(url);
    // 确保返回的数据格式正确
    if (Array.isArray(response.data)) {
      return response.data;
    } else if (response.data.result) {
      return {
        task_id: response.data.task_id,
        status: response.data.status,
        message: response.data.message,
        result: response.data.result,
      };
    }
    return response.data;
  } catch (error) {
    console.error("获取任务状态失败:", error);
    throw error;
  }
};

export const deleteTask = async (taskId) => {
  const response = await api.delete(`/tasks/${taskId}`);
  return response.data;
};

export const startAnalyze = async (taskId, strategy = "top50") => {
  try {
    console.log("发起分析请求:", { task_id: taskId, strategy }); // 添加请求日志
    const response = await api.post("/analyze", { task_id: taskId, strategy });
    return response.data;
  } catch (error) {
    console.error("分析请求失败:", error);
    throw error;
  }
};

export const getAnalysisResults = async (taskId) => {
  try {
    const response = await api.get(`/analysis/${taskId}`);
    return response.data;
  } catch (error) {
    console.error("获取分析结果失败:", error);
    throw error;
  }
};
