<script setup>
import { ref, reactive, onMounted, watch, onBeforeUnmount } from "vue";
import { getExpertModelAlarmInfo } from "@/api/expertModel";
import { formatDate, alarmCodeToStatus, formatText } from "@/utils";
import ExpertAlarmTable from "@/components/ExpertAlarmTable.vue";

const data = ref([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const form = reactive({
  include: "",
  exclude: "",
});

// last 30 days
const historyDataTimeRange = ref([
  // new Date(new Date().getTime() - 3600 * 1000 * 24 * 30),
  new Date(new Date().getTime() - 3600 * 1000 * 24 * 1),
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

const setData = async () => {
  const startTime = formatDate(historyDataTimeRange.value[0]);
  const endTime = formatDate(historyDataTimeRange.value[1]);
  console.log(startTime, endTime);
  const res = await getExpertModelAlarmInfo(
    form.include,
    form.exclude,
    startTime,
    endTime,
    currentPage.value,
    pageSize.value,
  );
  console.log(res);
  if (res.code === 200) {
    data.value = res.data
      .map((item) => {
        return {
          path: item.path,
          // path: item.path.split("_")[item.path.split("_").length - 1],
          device: item.device,
          alarm_report_path: item.alarm_report_path,
          predict_time: item.predict_time?.replace("T", " ").split(".")[0],
          status: alarmCodeToStatus(item.status),
          message: item.message,
        };
      })
      .sort((a, b) => {
        return new Date(b.predict_time) - new Date(a.predict_time);
      });
    total.value = res.total;
  }
};
const handleCurrentChange = (val) => {
  currentPage.value = val;
  setData();
};

watch(
  () => form,
  () => {
    setData();
  },
  { deep: true },
);
onMounted(() => {
  setData();
});
let interval = null;
onMounted(() => {
  setData();
  interval = setInterval(() => {
    setData();
  }, 30000);
});

onBeforeUnmount(() => {
  clearInterval(interval);
});
</script>

<template>
  <!-- 搜索框 -->
  <div class="input_box">
    <el-form :inline="true" :model="form" class="demo-form-inline">
      <el-form-item label="包含">
        <el-input
          style="width: 270px"
          v-model="form.include"
          placeholder="请输入include关键字"
        ></el-input>
      </el-form-item>
      <el-form-item label="排除">
        <el-input
          style="width: 270px"
          v-model="form.exclude"
          placeholder="请输入exclude关键字"
        ></el-input>
      </el-form-item>
      <el-form-item>
        <el-date-picker
          v-model="historyDataTimeRange"
          type="datetimerange"
          :shortcuts="shortcuts"
          range-separator="To"
          start-placeholder="Start date"
          end-placeholder="End date"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="setData">更新数据</el-button>
        <TrainAllButton :data="data" :set-data="setData" />
      </el-form-item>
    </el-form>
  </div>

  <div class="">
    <div class="table-box">
      <ExpertAlarmTable :data="data" :title="告警历史" @set-data="setData" />
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          background
          :total="total"
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 30, 50]"
          layout="prev, pager, next, sizes"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<style scoped></style>
