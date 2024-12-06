<script setup>
import { getSingleModelDetailByKey } from "@/api/singleModel";
import { ref, reactive } from "vue";
import { trainSingleModel } from "@/api/singleModel";
import {
  tableRowClassName,
  alarmCodeToStatus,
  formatDate,
  formatText,
} from "@/utils";
import { getHistoryDataByTime, getMeasuresInfoByKey } from "@/api/measures";
import { ElNotification, ElMessage } from "element-plus";
import * as echarts from "echarts";

const emit = defineEmits(["setData"]);

const key_store = ref("");

const historyDataDrawerVisible = ref(false);
const historyDataChart = ref();
let historyDataChartInstance = null;
const historyDataDrawerData = reactive({
  data: [],
});

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
    formatDate(trainDataTimeRange.value[0]),
    formatDate(trainDataTimeRange.value[1]),
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

const handleOpenHistoryDataDrawer = () => {
  historyDataChartInstance = echarts.init(historyDataChart.value);
  window.addEventListener("resize", () => {
    historyDataChartInstance.resize();
  });
};

const handleCloseHistoryDataDrawer = () => {
  historyDataChartInstance.dispose();
};

const handleViewHistoryDataDrawer = async (key) => {
  historyDataDrawerVisible.value = true;
  key_store.value = key;
  setHistoryData();
};

const setHistoryData = async () => {
  const res = await getHistoryDataByTime(
    key_store.value,
    formatDate(historyDataTimeRange.value[0]),
    formatDate(historyDataTimeRange.value[1]),
  );
  if (res.code === 200) {
    const historyData = res.data
      .map((item) => {
        return {
          fresh_time: item.fresh_time?.replace("T", " ").split(".")[0],
          time: item.time?.replace("T", " ").split(".")[0],
          service_time: item.service_time?.replace("T", " ").split(".")[0],
          value: item.value,
        };
      })
      .sort((a, b) => {
        return new Date(a.service_time) - new Date(b.service_time);
      });
    historyDataDrawerData.data = historyData;
    historyDataChartInstance.setOption({
      title: {
        text: "历史数据",
        left: "center",
        textStyle: {
          color: "#ccc",
          fontSize: 16,
        },
      },
      tooltip: {
        trigger: "axis",
        axisPointer: {
          type: "cross",
        },
      },
      xAxis: {
        type: "category",
        data: historyData.map((item) => item.time),
      },
      yAxis: {
        type: "value",
        min:
          Math.min(...historyData.map((item) => item.value)) -
          (Math.max(...historyData.map((item) => item.value)) -
            Math.min(...historyData.map((item) => item.value))) *
          0.2,
        max:
          Math.max(...historyData.map((item) => item.value)) +
          (Math.max(...historyData.map((item) => item.value)) -
            Math.min(...historyData.map((item) => item.value))) *
          0.2,
        splitLine: {
          show: false,
        },
      },
      series: [
        {
          data: historyData.map((item) => item.value),
          type: "line",
          smooth: true,
        },
      ],
    });
  }
};

const handleViewModelReport = async (key) => {
  const res = await getSingleModelDetailByKey(key);
  if (res.code === 200) {
    modelReportDialogData.report_path =
      "/minio-api/power-prophet/" + res.data.report_path;
    console.log(modelReportDialogData.report_path);
    modelReportDialogVisible.value = true;
  }
};
</script>

<template>
  <div>
    <h1>{{ props.title }}</h1>
    <el-table :data="props.data" border style="width: 100%" :row-class-name="tableRowClassName">
      <el-table-column prop="key" label="测点编号" align="center" width="240" />
      <el-table-column prop="path" label="测点" align="center" />
      <el-table-column prop="time" label="时间" align="center" width="220" />
      <el-table-column prop="value" label="值" align="center" width="120" />
      <el-table-column prop="unit" label="单位" align="center" width="80" />
      <el-table-column prop="status" label="状态" align="center" width="110" />
      <el-table-column prop="message" label="诊断信息" align="center" width="180">
        <template #default="{ row }">
          <div v-html="formatText(row.message)"></div>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" fixed="right" width="320">
        <template #default="scope">
          <el-button type="danger" @click="handleTrain(scope.row.key)">训练模型</el-button>
          <el-button @click="handleViewModelReport(scope.row.key)">模型报告</el-button>
          <el-button @click="handleViewHistoryDataDrawer(scope.row.key)">历史数据</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 历史数据抽屉 -->
    <el-drawer v-model="historyDataDrawerVisible" title="历史数据" size="40%" @open="handleOpenHistoryDataDrawer"
      @closed="handleCloseHistoryDataDrawer">
      <el-date-picker v-model="historyDataTimeRange" type="datetimerange" :shortcuts="shortcuts" range-separator="To"
        start-placeholder="Start date" end-placeholder="End date" />
      <el-button @click="setHistoryData">查询</el-button>
      <el-divider></el-divider>
      <div ref="historyDataChart" style="width: 100%; height: 300px"></div>
      <el-table :data="historyDataDrawerData.data" border style="width: 100%" height="650">
        <el-table-column prop="fresh_time" label="刷新时间" align="center" />
        <el-table-column prop="time" label="时间" align="center" />
        <el-table-column prop="value" label="值" align="center" />
      </el-table>
    </el-drawer>

    <!-- 模型报告弹窗 -->
    <el-dialog v-model="modelReportDialogVisible" modal="false" width="80%" align-center="true" show-close="false">
      <iframe :src="modelReportDialogData.report_path" width="100%" height="800"></iframe>
    </el-dialog>
  </div>
</template>

<style scoped>
span {
  display: flex;
  font-size: 16px;
}
</style>
