<template>
  <el-dialog v-model="dialogVisible" title="新增每日数据" width="500px">
    <el-form ref="formRef" :model="form" label-width="120px">
      <el-form-item label="Cookie" required>
        <el-input
          v-model="form.cookie"
          type="textarea"
          :rows="3"
          placeholder="请输入Cookie"
        />
      </el-form-item>
      <el-form-item label="Authorization" required>
        <el-input
          v-model="form.authorization"
          placeholder="请输入Bearer Token"
          :prefix-icon="Key"
        />
      </el-form-item>
      <el-form-item label="商品类别">
        <el-select
          v-model="form.category_id"
          placeholder="请选择商品类别"
          clearable
          style="width: 100%"
        >
          <el-option
            v-for="category in categories"
            :key="category.id"
            :label="category.name"
            :value="category.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="关键词">
        <el-input
          v-model="form.keyword"
          placeholder="请输入搜索关键词（选填）"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="handleSubmit"> 确认 </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, computed } from "vue";
import { ElMessage } from "element-plus";
import { Key } from "@element-plus/icons-vue";
import { createTask } from "../api";

const categories = [
  { id: "601450", name: "护理和美容" },
  { id: "601152", name: "女士服装" },
  { id: "824328", name: "男士服装" },
  { id: "600001", name: "家居用品" },
  { id: "605248", name: "时尚配饰" },
  { id: "601739", name: "手机和电子产品" },
  { id: "601303", name: "穆斯林时尚" },
  { id: "824584", name: "箱包" },
  { id: "601352", name: "鞋子" },
  { id: "602284", name: "婴儿与孕妇" },
  { id: "600024", name: "厨房用具" },
  { id: "603014", name: "运动和户外" },
  { id: "700437", name: "食品与饮料" },
  { id: "601755", name: "计算机与办公设备" },
  { id: "604206", name: "玩具和爱好" },
  { id: "802184", name: "儿童时尚" },
  { id: "605196", name: "汽车和摩托车" },
  { id: "602118", name: "宠物用品" },
  { id: "600942", name: "家用电器" },
  { id: "600154", name: "纺织和软家居" },
  { id: "604968", name: "家装" },
  { id: "604579", name: "五金工具" },
  { id: "801928", name: "书/杂志/影音" },
  { id: "700645", name: "健康" },
  { id: "953224", name: "珠宝饰品" },
  { id: "604453", name: "家具" },
  { id: "951432", name: "收藏" },
  { id: "834312", name: "虚拟商品" },
  { id: "0", name: "其他" },
];

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
});

const emit = defineEmits(["update:modelValue", "success"]);

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

const form = reactive({
  cookie: "",
  authorization: "",
  category_id: "",
  keyword: "",
});

const closeDialog = () => {
  emit("update:modelValue", false);
  // 重置表单
  form.cookie = "";
  form.authorization = "";
  form.category_id = "";
  form.keyword = "";
};

const validateForm = () => {
  if (!form.cookie.trim()) {
    ElMessage.warning("请输入Cookie");
    return false;
  }
  if (!form.authorization.trim()) {
    ElMessage.warning("请输入Authorization");
    return false;
  }
  if (!form.category_id && !form.keyword) {
    ElMessage.warning("请至少选择商品类别或输入关键词其中之一");
    return false;
  }
  return true;
};

const handleSubmit = async () => {
  if (!validateForm()) return;

  try {
    // 确保authorization格式正确
    const token = form.authorization.trim();
    const formattedAuth = token.startsWith("Bearer ")
      ? token
      : `Bearer ${token}`;

    const result = await createTask({
      ...form,
      authorization: formattedAuth,
    });

    emit("success", result.task_id);
    closeDialog();
    ElMessage.success("任务创建成功");
  } catch (error) {
    // 错误处理已经在 api 拦截器中统一处理
    console.error("创建任务失败:", error);
  }
};
</script>

<style lang="less" scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-form-item) {
  margin-bottom: 22px;

  &:last-child {
    margin-bottom: 0;
  }
}
</style>
