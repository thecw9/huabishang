<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { trainSingleModel } from "@/api/singleModel";
import { ElNotification, ElMessage } from "element-plus";
import {
  formatDate,
} from "@/utils";

const emit = defineEmits(["setData"]);

const router = useRouter();

const dialogVisible = ref(false);
const trainDataTimeRange = ref([
  new Date(new Date().getTime() - 3600 * 1000 * 24 * 30),
  new Date(),
]);

const shortcuts = [
  {
    text: "Today",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setHours(0);
      start.setMinutes(0);
      start.setSeconds(0);
      return [start, end];
    },
  },
  {
    text: "Last 1 day",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24);
      return [start, end];
    },
  },
  {
    text: "Last week",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
      return [start, end];
    },
  },
  {
    text: "Last month",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
      return [start, end];
    },
  },
  {
    text: "Last 3 months",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
      return [start, end];
    },
  },
];

const props = defineProps({
  data: {
    type: Object,
    default: () => [],
  },
});

const handleViewTrainLogs = () => {
  // 跳转到/train-logs
  router.push("/train_logs");
};

const handleTrainAll = async () => {
  const error_train_key = [];
  const success_train_key = [];
  props.data.forEach(async (item) => {
    const res = await trainSingleModel(
      item.key,
      formatDate(trainDataTimeRange.value[0]),
      formatDate(trainDataTimeRange.value[1]),
    );
    if (res.code !== 200) {
      error_train_key.push(item.key);
      ElMessage.error(`模型${item.key}训练失败`);
    } else {
      success_train_key.push(item.key);
      ElMessage.success(`模型${item.key}训练成功`);
    }
  });

  dialogVisible.value = false;
  // sleep 1s
  await new Promise((resolve) => {
    setTimeout(() => {
      resolve();
    }, 500);
  });
  emit("setData");
};
</script>

<template>
  <el-button type="primary" @click="dialogVisible = true">全部训练</el-button>

  <!-- 全部训练弹窗 -->
  <el-dialog v-model="dialogVisible" title="训练模型" width="50%">
    <span style="margin-bottom: 10px; font-size: 18px">选择训练数据时间范围：</span>
    <el-date-picker v-model="trainDataTimeRange" type="datetimerange" :shortcuts="shortcuts" range-separator="To"
      start-placeholder="Start date" end-placeholder="End date" />
    <template #footer>
      <span class="dialog-footer">
        <el-button class="cancel-btn" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleTrainAll">确认训练</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<style scoped>
.header {
  width: 100%;
  height: 60px;
  background-color: #545c6410;
  @apply flex items-center;
}

.breadcrumb_text {
  color: #fff;

  &:hover {
    color: #409eff;
  }
}

.exit-btn {
  position: absolute;
  right: 20px;
}
</style>
