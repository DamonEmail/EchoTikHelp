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
        <el-button type="primary" @click="handleRefresh" :icon="Refresh">
          刷新
        </el-button>
      </div>
    </div>

    <el-table :data="tasks" style="width: 100%" v-loading="isRefreshing">
      <el-table-column prop="task_id" label="任务ID" width="200">
        <template #default="{ row }">
          <el-link
            type="primary"
            @click="handleRowClick(row)"
            :underline="false"
          >
            {{ row.task_id }}
          </el-link>
        </template>
      </el-table-column>
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
                <el-tooltip :content="row.result.file_name" placement="top">
                  <span class="file-name">{{
                    getShortFileName(row.result.file_name)
                  }}</span>
                </el-tooltip>
                <el-tag size="small" effect="plain">原始数据</el-tag>
              </el-link>
            </template>
            <template v-if="row.result?.analysis_file">
              <el-link type="success" @click="handleDownload(row, 'analysis')">
                <el-tooltip :content="row.result.analysis_file" placement="top">
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
              v-if="row.status !== 'analyzing' && row.result?.file_path"
              type="primary"
              size="small"
              :icon="DataAnalysis"
              circle
              plain
              @click="handleAnalyzeClick(row)"
            />
            <el-button
              v-else-if="row.status === 'analyzing'"
              type="warning"
              size="small"
              :loading="true"
              circle
              plain
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

    <analysis-results
      v-if="selectedTask && selectedTask.result?.analysis_json"
      :task-id="selectedTask.task_id"
      :visible="!!selectedTask"
      @close="selectedTask = null"
    />

    <analyze-dialog
      v-model="showAnalyzeDialog"
      :task-id="currentTask?.task_id"
      :file-name="currentTask?.result?.file_name"
      @success="handleAnalyzeSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, watch, onMounted } from "vue";
import { getTaskStatus, deleteTask, startAnalyze } from "../api";
import { ElMessage } from "element-plus";
import { Delete, DataAnalysis, Refresh } from "@element-plus/icons-vue";
import AnalyzeDialog from "./AnalyzeDialog.vue";
import AnalysisResults from "./AnalysisResults.vue";

const props = defineProps({
  tasks: Array,
});

const emit = defineEmits(["update:tasks"]);

const autoRefresh = ref(false);
const isRefreshing = ref(false);
let timer = null;

const showAnalyzeDialog = ref(false);
const currentTask = ref(null);
const selectedTask = ref(null);

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
  console.log("Refreshing tasks...");
  try {
    isRefreshing.value = true;
    const response = await getTaskStatus();
    console.log("API Response:", response);

    if (Array.isArray(response)) {
      emit("update:tasks", response);

      // 检查分析完成的任务
      response.forEach((task) => {
        console.log("Processing task:", task); // 添加调试日志
        if (task.status === "completed" && task.result?.analysis_file) {
          const oldTask = props.tasks.find((t) => t.task_id === task.task_id);
          if (oldTask?.status === "analyzing") {
            ElMessage.success(
              `任务 ${getShortFileName(task.result.file_name)} 分析完成`
            );
          }
        }
      });
    }
  } catch (error) {
    console.error("刷新任务状态失败:", error);
    throw error;
  } finally {
    isRefreshing.value = false;
  }
};

const getStatusType = (status) => {
  switch (status) {
    case "pending":
      return "info";
    case "running":
    case "analyzing": // 添加分析中状态
      return "warning";
    case "completed":
      return "success";
    case "failed":
      return "danger";
    default:
      return "info";
  }
};

const getStatusText = (status) => {
  switch (status) {
    case "pending":
      return "等待中";
    case "running":
      return "运行中";
    case "analyzing": // 添加分析中状态
      return "分析中";
    case "completed":
      return "已完成";
    case "failed":
      return "失败";
    default:
      return "未知";
  }
};

const handleDownload = (task, type = "raw") => {
  const filePath =
    type === "analysis" ? task.result?.analysis_file : task.result?.file_path;
  if (filePath) {
    window.open(
      `http://localhost:9527/api/download/${task.task_id}?type=${type}`
    );
  }
};

const handleDelete = async (task) => {
  try {
    isRefreshing.value = true;
    await deleteTask(task.task_id);
    emit(
      "update:tasks",
      props.tasks.filter((t) => t.task_id !== task.task_id)
    );
    ElMessage.success("任务已删除");
    if (selectedTask.value?.task_id === task.task_id) {
      selectedTask.value = null;
    }
  } catch (error) {
    console.error("删除任务失败:", error);
    ElMessage.error(error.response?.data?.detail || "删除任务失败，请稍后重试");
  } finally {
    isRefreshing.value = false;
  }
};

const handleAnalyzeClick = (task) => {
  if (task.status === "analyzing") {
    ElMessage.warning("任务正在分析中，请稍后...");
    return;
  }
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

onMounted(async () => {
  try {
    console.log("初始化加载任务列表...");
    await handleRefresh();
  } catch (error) {
    console.error("初始化加载失败:", error);
    ElMessage.error("加载任务列表失败，请刷新页面重试");
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

// 处理行点击
const handleRowClick = (row) => {
  // 只有已完成且有分析结果的任务才能查看
  if (row.result?.analysis_json) {
    // 如果点击的是当前选中的任务，则关闭展示
    if (selectedTask.value?.task_id === row.task_id) {
      selectedTask.value = null;
      return;
    }
    selectedTask.value = row;
  } else if (row.result?.file_path) {
    ElMessage.info("该任务尚未进行分析，请先点击分析按钮");
  } else {
    ElMessage.info(`任务${getStatusText(row.status)}，暂无分析结果`);
  }
};

// 监听分析完成事件
watch(
  () => props.tasks,
  (newTasks) => {
    // 如果当前有选中的任务，更新其数据
    if (selectedTask.value) {
      const updatedTask = newTasks.find(
        (t) => t.task_id === selectedTask.value.task_id
      );
      if (updatedTask) {
        selectedTask.value = updatedTask;
      }
    }
  },
  { deep: true }
);
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

      &:hover {
        text-decoration: underline;
      }
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
