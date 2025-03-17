<template>
  <div class="app-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <div class="logo">
            <img src="./assets/logo.png" alt="logo" />
            <h1>嘀嗒狗日常数据分析助手</h1>
          </div>
          <el-button
            type="primary"
            size="large"
            :icon="Plus"
            class="add-button"
            @click="showNewTaskDialog = true"
          >
            新增数据分析
          </el-button>
        </div>
      </el-header>

      <el-main>
        <div class="main-content">
          <task-list v-model:tasks="tasks" />
        </div>
      </el-main>

      <el-footer>
        <p>© 2024 嘀嗒狗数据分析助手 v1.0.0</p>
      </el-footer>
    </el-container>

    <new-task-dialog v-model="showNewTaskDialog" @success="handleTaskCreated" />
  </div>
</template>

<script setup>
import { ref } from "vue";
import { Plus } from "@element-plus/icons-vue";
import TaskList from "./components/TaskList.vue";
import NewTaskDialog from "./components/NewTaskDialog.vue";

const showNewTaskDialog = ref(false);
const tasks = ref([]);

const handleTaskCreated = (taskId) => {
  tasks.value.unshift({
    task_id: taskId,
    status: "pending",
    message: "任务已创建，正在启动...",
  });
};
</script>

<style lang="less">
:root {
  --primary-color: #409eff;
  --header-height: 64px;
  --footer-height: 50px;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  background-color: #f5f7fa;
}

.app-container {
  min-height: 100vh;

  .el-container {
    min-height: 100vh;
  }

  .el-header {
    background: linear-gradient(135deg, var(--primary-color), #79bbff);
    padding: 0;
    height: var(--header-height) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

    .header-content {
      max-width: 1200px;
      margin: 0 auto;
      height: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 20px;

      .logo {
        display: flex;
        align-items: center;
        gap: 12px;

        img {
          height: 40px;
          width: 40px;
          object-fit: contain;
        }

        h1 {
          color: white;
          font-size: 20px;
          margin: 0;
          font-weight: 600;
        }
      }

      .add-button {
        background-color: white;
        color: var(--primary-color);
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;

        &:hover {
          background-color: #ecf5ff;
          transform: translateY(-2px);
        }
      }
    }
  }

  .el-main {
    padding: 0;

    .main-content {
      max-width: 1200px;
      margin: 0 auto;
      padding: 24px;
      min-height: calc(100vh - var(--header-height) - var(--footer-height));
    }
  }

  .el-footer {
    height: var(--footer-height) !important;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: white;
    color: #909399;
    font-size: 14px;
    border-top: 1px solid #e4e7ed;
  }
}

// 全局样式优化
.el-table {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);

  .el-table__header {
    background-color: #f5f7fa;
  }
}

.el-dialog {
  border-radius: 8px;

  .el-dialog__header {
    margin: 0;
    padding: 20px;
    border-bottom: 1px solid #e4e7ed;
  }

  .el-dialog__body {
    padding: 24px;
  }

  .el-dialog__footer {
    border-top: 1px solid #e4e7ed;
    padding: 16px 20px;
  }
}
</style>
