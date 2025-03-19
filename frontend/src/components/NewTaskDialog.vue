<template>
  <el-dialog v-model="dialogVisible" title="新增每日数据" width="500px">
    <el-form ref="formRef" :model="form" label-width="120px">
      <el-form-item label="Cookie" prop="cookie">
        <el-input
          v-model="form.cookie"
          type="textarea"
          :rows="3"
          placeholder="请输入Cookie"
        />
      </el-form-item>
      <el-form-item label="Authorization" prop="authorization">
        <el-input
          v-model="form.authorization"
          type="textarea"
          :rows="2"
          placeholder="请输入Authorization"
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
        <el-button @click="handleReset">重置凭证</el-button>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleConfirm"
          :loading="isSubmitting"
        >
          确认
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
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

const isSubmitting = ref(false);
const formRef = ref(null);

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

const form = ref({
  cookie: localStorage.getItem("echotik_cookie") || "",
  authorization: localStorage.getItem("echotik_auth") || "",
  category_id: "",
  keyword: "",
});

const rules = {
  cookie: [{ required: true, message: "请输入Cookie", trigger: "blur" }],
  authorization: [
    { required: true, message: "请输入Authorization", trigger: "blur" },
  ],
};

const closeDialog = () => {
  emit("update:modelValue", false);
  // 重置表单
  form.value.cookie = "";
  form.value.authorization = "";
  form.value.category_id = "";
  form.value.keyword = "";
};

const validateForm = () => {
  if (!form.value.cookie.trim()) {
    ElMessage.warning("请输入Cookie");
    return false;
  }
  if (!form.value.authorization.trim()) {
    ElMessage.warning("请输入Authorization");
    return false;
  }
  if (!form.value.category_id && !form.value.keyword) {
    ElMessage.warning("请至少选择商品类别或输入关键词其中之一");
    return false;
  }
  return true;
};

const handleConfirm = async () => {
  if (!formRef.value) return;

  try {
    await formRef.value.validate();
    isSubmitting.value = true;

    // 保存凭证到本地存储
    localStorage.setItem("echotik_cookie", form.value.cookie);
    localStorage.setItem("echotik_auth", form.value.authorization);

    const response = await createTask({
      category_id: form.value.category_id || undefined,
      keyword: form.value.keyword || undefined,
      cookie: form.value.cookie,
      authorization: form.value.authorization,
    });

    ElMessage.success("任务创建成功");
    emit("update:modelValue", false);
    emit("success", response);
  } catch (error) {
    console.error("创建任务失败:", error);
  } finally {
    isSubmitting.value = false;
  }
};

const handleReset = () => {
  // 清除本地存储的凭证
  localStorage.removeItem("echotik_cookie");
  localStorage.removeItem("echotik_auth");

  // 清空表单中的凭证字段
  form.value.cookie = "";
  form.value.authorization = "";

  ElMessage.success("凭证已重置");
};

const show = () => {
  emit("update:modelValue", true);
  // 重置表单数据，但保留凭证
  const savedCookie = form.value.cookie;
  const savedAuth = form.value.authorization;
  if (formRef.value) {
    formRef.value.resetFields();
  }
  // 恢复凭证
  form.value.cookie = savedCookie;
  form.value.authorization = savedAuth;
};

defineExpose({
  show,
});
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
