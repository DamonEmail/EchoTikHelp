const refreshTasks = async () => { try { const response = await getTaskStatus();
if (Array.isArray(response)) { tasks.value = response; } else { tasks.value =
[]; } } catch (error) { console.error("刷新任务列表失败:", error);
ElMessage.error("刷新任务列表失败，请稍后重试"); } };
