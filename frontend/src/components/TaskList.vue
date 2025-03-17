<template>
  <div class="task-list">
    <div class="task-header">
      <h2>任务列表</h2>
      <div class="task-actions">
        <el-switch
          v-model="autoRefresh"
          active-text="自动刷新"
          :disabled="!hasRunningTasks"
        />
        <el-button
          type="primary"
          @click="handleRefresh"
          :loading="isRefreshing"
          :disabled="isRefreshing"
        >
          刷新
        </el-button>
      </div>
    </div>

    <el-table :data="tasks" style="width: 100%" v-loading="isRefreshing">
      <el-table-column prop="task_id" label="任务ID" width="200" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="message" label="消息" />
      <el-table-column label="文件" width="300">
        <template #default="{ row }">
          <div class="file-list">
            <template v-if="row.result?.file_name">
              <el-link type="primary" @click="handleDownload(row, 'raw')">
                <el-tooltip
                  :content="row.result.file_name"
                  placement="top"
                  :show-after="500"
                >
                  <span class="file-name">{{
                    getShortFileName(row.result.file_name)
                  }}</span>
                </el-tooltip>
              </el-link>
            </template>
            <template v-if="row.result?.analysis_file">
              <el-link type="success" @click="handleDownload(row, 'analysis')">
                <el-tooltip
                  :content="row.result.analysis_file"
                  placement="top"
                  :show-after="500"
                >
                  <span class="file-name">{{
                    getShortFileName(row.result.analysis_file)
                  }}</span>
                </el-tooltip>
                <el-tag size="small" effect="plain" type="success"
                  >分析结果</el-tag
                >
              </el-link>
            </template>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button
              v-if="row.status === 'completed'"
              type="primary"
              size="small"
              :icon="DataAnalysis"
              circle
              plain
              @click="handleAnalyzeClick(row)"
            />
            <el-popconfirm
              :title="`确定要删除此任务吗？${
                row.result?.file_path ? '相关数据文件也会被删除。' : ''
              }`"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button
                  type="danger"
                  size="small"
                  :icon="Delete"
                  circle
                  plain
                />
              </template>
            </el-popconfirm>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <analyze-dialog
      v-model="showAnalyzeDialog"
      :task-id="currentTask?.task_id"
      :file-name="currentTask?.result?.file_name"
      @success="handleAnalyzeSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, watch } from "vue";
import { getTaskStatus, deleteTask } from "../api";
import { ElMessage } from "element-plus";
import { Delete, DataAnalysis } from "@element-plus/icons-vue";
import AnalyzeDialog from "./AnalyzeDialog.vue";

const props = defineProps({
  tasks: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(["update:tasks"]);

const autoRefresh = ref(false);
const isRefreshing = ref(false);
let timer = null;

const showAnalyzeDialog = ref(false);
const currentTask = ref(null);

// 计算是否有正在运行的任务
const hasRunningTasks = computed(() => {
  return props.tasks.some((task) =>
    ["pending", "running", "analyzing"].includes(task.status)
  );
});

// 监听运行状态，当没有运行中的任务时，关闭自动刷新
watch(hasRunningTasks, (newValue) => {
  if (!newValue && autoRefresh.value) {
    autoRefresh.value = false;
    ElMessage.success("所有任务已完成");
  }
});

const handleRefresh = async () => {
  if (isRefreshing.value) return;

  try {
    isRefreshing.value = true;
    const updatedTasks = await Promise.all(
      props.tasks.map(async (task) => {
        // 检查需要更新状态的任务
        if (["pending", "running", "analyzing"].includes(task.status)) {
          try {
            return await getTaskStatus(task.task_id);
          } catch (error) {
            console.error(`获取任务 ${task.task_id} 状态失败:`, error);
            return task;
          }
        }
        return task;
      })
    );

    // 检查是否有状态变化
    const hasChanges = updatedTasks.some((newTask, index) => {
      const oldTask = props.tasks[index];
      return (
        oldTask.status !== newTask.status ||
        oldTask.message !== newTask.message ||
        JSON.stringify(oldTask.result) !== JSON.stringify(newTask.result)
      );
    });

    if (hasChanges) {
      emit("update:tasks", updatedTasks);

      // 检查分析完成的任务
      updatedTasks.forEach((task, index) => {
        const oldTask = props.tasks[index];
        if (
          oldTask.status === "analyzing" &&
          task.status === "completed" &&
          task.result?.analysis_file
        ) {
          ElMessage.success(
            `任务 ${getShortFileName(task.result.file_name)} 分析完成`
          );
        }
      });
    }
  } catch (error) {
    console.error("刷新任务状态失败:", error);
    ElMessage.error("刷新任务状态失败，请稍后重试");
  } finally {
    isRefreshing.value = false;
  }
};

const getStatusType = (status) => {
  const map = {
    pending: "info",
    running: "warning",
    analyzing: "warning",
    completed: "success",
    failed: "danger",
  };
  return map[status] || "info";
};

const getStatusText = (status) => {
  const map = {
    pending: "等待中",
    running: "进行中",
    analyzing: "分析中",
    completed: "已完成",
    failed: "失败",
  };
  return map[status] || status;
};

const handleDownload = (task, type = "raw") => {
  const filePath =
    type === "analysis" ? task.result?.analysis_file : task.result?.file_path;
  if (filePath) {
    window.open(
      `http://localhost:8000/api/download/${task.task_id}?type=${type}`
    );
  }
};

const handleDelete = async (task) => {
  try {
    await deleteTask(task.task_id);
    emit(
      "update:tasks",
      props.tasks.filter((t) => t.task_id !== task.task_id)
    );
    ElMessage.success("任务已删除");
  } catch (error) {
    console.error("删除任务失败:", error);
    ElMessage.error("删除任务失败，请稍后重试");
  }
};

const handleAnalyzeClick = (task) => {
  currentTask.value = task;
  showAnalyzeDialog.value = true;
};

const handleAnalyzeSuccess = () => {
  handleRefresh(); // 刷新任务状态
};

// 自动刷新逻辑
watch(autoRefresh, (newValue) => {
  if (newValue && hasRunningTasks.value) {
    timer = window.setInterval(handleRefresh, 3000);
  } else if (timer) {
    clearInterval(timer);
    timer = null;
  }
});

onUnmounted(() => {
  if (timer) {
    clearInterval(timer);
  }
});

// 文件名显示优化
const getShortFileName = (fileName) => {
  if (!fileName) return "";
  const maxLength = 30;
  return fileName.length > maxLength
    ? fileName.slice(0, maxLength - 3) + "..."
    : fileName;
};
</script>

<style lang="less" scoped>
.task-list {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  padding: 24px;

  .task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    h2 {
      margin: 0;
      font-size: 18px;
      color: #303133;
      font-weight: 600;
    }

    .task-actions {
      display: flex;
      gap: 16px;
      align-items: center;

      .el-switch {
        --el-switch-on-color: var(--primary-color);
      }

      .el-button {
        padding: 8px 16px;
      }
    }
  }

  :deep(.el-table) {
    .el-tag {
      border-radius: 4px;
      padding: 0 8px;
      height: 24px;
      line-height: 24px;
    }

    .el-link {
      font-size: 13px;
    }
  }

  .action-buttons {
    display: flex;
    gap: 8px;
  }

  .file-list {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .el-link {
      display: flex;
      align-items: center;
      gap: 8px;
      max-width: 100%;

      .file-name {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }
}
</style>
