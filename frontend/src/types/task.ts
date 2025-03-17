export interface TaskRequest {
  category_id?: string;
  keyword?: string;
  cookie?: string;
}

export interface TaskStatus {
  task_id: string;
  status: "pending" | "running" | "completed" | "failed";
  message: string;
  result?: {
    file_path: string;
    file_name: string;
  };
}
