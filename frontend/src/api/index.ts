import axios from "axios";
import type { TaskRequest, TaskStatus } from "../types/task";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
});

export const createTask = async (data: TaskRequest) => {
  const response = await api.post<TaskStatus>("/crawl", data);
  return response.data;
};

export const getTaskStatus = async (taskId: string) => {
  const response = await api.get<TaskStatus>(`/status/${taskId}`);
  return response.data;
};
