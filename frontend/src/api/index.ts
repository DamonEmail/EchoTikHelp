import axios from "axios";
import type { TaskRequest, TaskStatus } from "../types/task";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
});

export const createTask = async (data: TaskRequest) => {
  const response = await api.post<TaskStatus>("/crawl", data);
  return response.data;
};

export const getTaskStatus = async (taskId?: string) => {
  try {
    const response = await api.get<TaskStatus>(
      taskId ? `/status/${taskId}` : "/api/tasks"
    );
    return response.data;
  } catch (error) {
    console.error("获取任务状态失败:", error);
    throw error;
  }
};
