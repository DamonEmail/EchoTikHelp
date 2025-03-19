<template>
  <el-dialog
    :model-value="modelValue"
    :title="`自定义策略选品(${categoryName})`"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="!analyzing"
  >
    <div class="analyze-content">
      <h3>选择分析策略：</h3>
      <el-radio-group v-model="selectedStrategy" class="strategy-list">
        <el-radio label="top50" border style="height: auto">
          <div class="strategy-info">
            <h4>TOP50选品策略</h4>
            <p>1. 首先筛选价格范围内的有效商品</p>
            <p>2. 对7天销量进行排名评分（由高到低）</p>
            <p>3. 对达人数量进行排名评分（由低到高）</p>
          </div>
        </el-radio>
        <!-- 后续可以在这里添加更多策略 -->
      </el-radio-group>

      <div v-if="analyzing" class="analyze-progress">
        <el-progress type="circle" :percentage="analyzeProgress" />
        <p class="progress-text">{{ analyzeStatus }}</p>
      </div>

      <!-- 如果已有分析结果，显示提示 -->
      <el-alert
        v-if="props.taskId && hasExistingAnalysis"
        type="warning"
        :closable="false"
        style="margin-bottom: 15px"
      >
        该任务已有分析结果，重新分析将覆盖现有结果
      </el-alert>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose" :disabled="analyzing">取消</el-button>
        <el-button
          type="primary"
          :loading="analyzing"
          :disabled="!selectedStrategy || analyzing"
          @click="handleConfirm"
        >
          {{ analyzing ? "分析中..." : "开始分析" }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onUnmounted } from "vue";
import { ElMessage } from "element-plus";
import { startAnalyze } from "../api";

const props = defineProps({
  modelValue: Boolean,
  taskId: String,
  fileName: String,
  tasks: Array,
});

const emit = defineEmits(["update:modelValue", "success"]);

const analyzing = ref(false);
const selectedStrategy = ref("top50");
const analyzeProgress = ref(0);
const analyzeStatus = ref("");
let progressTimer = null;

// 从文件名解析类别
const categoryName = computed(() => {
  const categories = {
    601450: "护理和美容",
    601152: "女士服装",
    824328: "男士服装",
    600001: "家居用品",
    605248: "时尚配饰",
    601739: "手机和电子产品",
    601303: "穆斯林时尚",
    824584: "箱包",
    601352: "鞋子",
    602284: "婴儿与孕妇",
    600024: "厨房用具",
    603014: "运动和户外",
    700437: "食品与饮料",
    601755: "计算机与办公设备",
    604206: "玩具和爱好",
    802184: "儿童时尚",
    605196: "汽车和摩托车",
    602118: "宠物用品",
    600942: "家用电器",
    600154: "纺织和软家居",
    604968: "家装",
    604579: "五金工具",
    801928: "书/杂志/影音",
    700645: "健康",
    953224: "珠宝饰品",
    604453: "家具",
    951432: "收藏",
    834312: "虚拟商品",
    0: "其他",
  };

  const match = props.fileName?.match(/products_cat(\d+)_/);
  if (match) {
    const categoryId = match[1];
    return categories[categoryId] || "未知类别";
  }
  return "未知类别";
});

// 检查是否已有分析结果
const hasExistingAnalysis = computed(() => {
  const task = props.tasks?.find((t) => t.task_id === props.taskId);
  return task?.result?.analysis_file;
});

const handleClose = () => {
  if (analyzing.value) return;
  emit("update:modelValue", false);
};

const handleConfirm = async () => {
  try {
    analyzing.value = true;

    await startAnalyze(props.taskId, selectedStrategy.value);
    ElMessage.success("分析任务已启动");
    emit("success");
    emit("update:modelValue", false);
  } catch (error) {
    console.error("启动分析失败:", error);
    ElMessage.error(error.response?.data?.detail || "启动分析失败，请稍后重试");
  } finally {
    analyzing.value = false;
  }
};

onUnmounted(() => {
  // resetProgress();
});
</script>

<style lang="less" scoped>
.analyze-content {
  h3 {
    margin-top: 0;
    margin-bottom: 20px;
    font-size: 16px;
    color: #303133;
  }

  .strategy-list {
    display: flex;
    flex-direction: column;
    gap: 16px;

    .strategy-info {
      padding: 8px 0;

      h4 {
        margin: 0 0 8px;
        color: #303133;
      }

      p {
        margin: 4px 0;
        color: #606266;
        font-size: 13px;
      }
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.analyze-progress {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;

  .progress-text {
    color: #606266;
    font-size: 14px;
    margin: 0;
  }
}
</style>
