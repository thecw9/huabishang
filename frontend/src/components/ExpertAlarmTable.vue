<script setup>
import { ref, reactive } from "vue";
import { tableRowClassName, formatText } from "@/utils";
import { ElNotification, ElMessage } from "element-plus";
import * as echarts from "echarts";

const emit = defineEmits(["setData"]);

const key_store = ref("");

const modelReportDialogVisible = ref(false);
const modelReportDialogData = reactive({
  report_path: "",
});

// last 30 days
const historyDataTimeRange = ref([
  // new Date(new Date().getTime() - 3600 * 1000 * 24 * 30),
  new Date(new Date().getTime() - 3600 * 1000 * 24 * 1),
  new Date(),
]);
const trainDataTimeRange = ref([
  new Date(new Date().getTime() - 3600 * 1000 * 24 * 30),
  new Date(),
]);

const shortcuts = [
  {
    text: "今天",
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
    text: "过去一天",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24);
      return [start, end];
    },
  },
  {
    text: "过去一周",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
      return [start, end];
    },
  },
  {
    text: "过去一个月",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
      return [start, end];
    },
  },
  {
    text: "过去三个月",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
      return [start, end];
    },
  },
];

const props = defineProps({
  title: {
    type: String,
    default: "",
  },
  data: {
    type: Object,
    default: () => [],
  },
});

const handleTrain = async (key) => {
  const res = await trainSingleModel(
    key,
    trainDataTimeRange.value[0],
    trainDataTimeRange.value[1],
  );
  if (res.code === 200) {
    ElNotification({
      title: "模型训练",
      message: "模型训练成功",
      type: "success",
    });
    // sleep 1s
    await new Promise((resolve) => {
      setTimeout(() => {
        resolve();
      }, 500);
    });
    emit("setData");
  } else {
    ElMessage.error("失败");
  }
};

const handleViewModelReport = async (alarm_report_path) => {
  modelReportDialogData.report_path =
    "/minio-api/power-prophet/" + alarm_report_path;
  console.log(modelReportDialogData.report_path);
  modelReportDialogVisible.value = true;
};
</script>

<template>
  <div>
    <h1>{{ props.title }}</h1>
    <el-table
      :data="props.data"
      border
      style="width: 100%"
      :row-class-name="tableRowClassName"
    >
      <el-table-column prop="path" label="测点" align="center" width="280" />
      <el-table-column
        prop="predict_time"
        label="预测时间"
        align="center"
        width="180"
      />
      <el-table-column prop="status" label="状态" align="center" />
      <el-table-column prop="message" label="诊断信息" width="800">
        <template #default="{ row }">
          <div v-html="formatText(row.message)"></div>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" fixed="right">
        <template #default="scope">
          <el-button @click="handleViewModelReport(scope.row.alarm_report_path)"
            >模型报告</el-button
          >
        </template>
      </el-table-column>
    </el-table>

    <!-- 模型报告弹窗 -->
    <el-dialog
      v-model="modelReportDialogVisible"
      modal="false"
      width="80%"
      align-center="true"
      show-close="false"
    >
      <iframe
        :src="modelReportDialogData.report_path"
        width="100%"
        height="800"
      ></iframe>
    </el-dialog>
  </div>
</template>

<style scoped>
span {
  display: flex;
  font-size: 16px;
}
</style>
