<script setup>
import { ref, reactive, onMounted, watch, onBeforeUnmount, provide } from "vue";
import { getExpertModelAlarmInfo, getExpertModelInfo } from "@/api/expertModel";
import WindTurbine from "./components/WindTurbine.vue";
import {
  formatDate,
  tableRowClassName,
  alarmCodeToStatus,
  formatText,
} from "@/utils";

const deviceDetailDialogVisible = ref(false);
const deviceDetail = ref([]);

const form = reactive({
  device: "",
  historyAlarmTimeRange: [
    // new Date(new Date().getTime() - 3600 * 1000 * 24 * 30),
    new Date(new Date().getTime() - 3600 * 1000 * 24 * 1),
    new Date(),
  ],
});

const devices = ref([
  {
    device: "#1号机组",
    status: -1,
  },
  {
    device: "#2号机组",
    status: -1,
  },
  {
    device: "#3号机组",
    status: -1,
  },
  {
    device: "#4号机组",
    status: -1,
  },
  {
    device: "#5号机组",
    status: -1,
  },
  {
    device: "#6号机组",
    status: -1,
  },
  {
    device: "#7号机组",
    status: -1,
  },
  {
    device: "#8号机组",
    status: -1,
  },
  {
    device: "#9号机组",
    status: -1,
  },
  {
    device: "#10号机组",
    status: -1,
  },
  {
    device: "#11号机组",
    status: -1,
  },
  {
    device: "#12号机组",
    status: -1,
  },
  {
    device: "#13号机组",
    status: -1,
  },
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

const alarmMessages = ref([]);

const setData = async () => {
  devices.value.forEach(async (item) => {
    await getExpertModelInfo(item.device).then((res) => {
      // await getExpertModelAlarmInfo(item.device).then((res) => {
      if (res.code === 200) {
        console.log(res.data);
        const max_status =
          res.data.length === 0
            ? -1
            : res.data.reduce((prev, current) =>
                prev.status > current.status ? prev : current,
              ).status;
        item.status = alarmCodeToStatus(max_status);
        item.message = res.data.map((item) => item.message).join("\n");
      }
    });
  });
};

const handleViewDetail = async (device) => {
  await getExpertModelAlarmInfo(
    device,
    "",
    formatDate(form.historyAlarmTimeRange[0]),
    formatDate(form.historyAlarmTimeRange[1]),
  ).then((res) => {
    if (res.code === 200) {
      deviceDetail.value = res.data
        .map((item) => {
          return {
            key: item._id,
            predict_time: item.predict_time,
            message: item.message,
            status: alarmCodeToStatus(item.status),
          };
        })
        .sort((a, b) => {
          return new Date(b.predict_time) - new Date(a.predict_time);
        });
    }
  });
  if (deviceDetail.value.length === 0) {
    deviceDetail.value = [
      {
        predict_time: new Date().toISOString(),
        message: "设备正常",
        status: "正常",
      },
    ];
  }
  deviceDetailDialogVisible.value = true;
};

const setAlarmData = async () => {
  const startTime = formatDate(form.historyAlarmTimeRange[0]);
  const endTime = formatDate(form.historyAlarmTimeRange[1]);
  await getExpertModelAlarmInfo(form.device, "", startTime, endTime).then(
    (res) => {
      if (res.code === 200) {
        alarmMessages.value = res.data
          .map((item) => {
            return {
              key: item._id,
              path: item.device,
              model_name: item.model_name,
              model_type: item.model_type,
              time: item.predict_time?.replace("T", " ").split(".")[0],
              device: item.device,
              status: alarmCodeToStatus(item.status),
              message: item.message,
            };
          })
          .sort((a, b) => {
            return new Date(b.time) - new Date(a.time);
          });
      }
    },
  );
};

let interval = null;
onMounted(() => {
  setData();
  setAlarmData();
  interval = setInterval(() => {
    form.historyAlarmTimeRange = [
      new Date(new Date().getTime() - 3600 * 1000 * 24 * 1),
      new Date(),
    ];
    setData();
    setAlarmData();
  }, 10000);
});

onBeforeUnmount(() => {
  clearInterval(interval);
});

watch(
  () => form,
  () => {
    setAlarmData();
  },
  { deep: true },
);
</script>

<template>
  <el-row>
    <div class="train-all">
      <el-form :inline="true" :model="form" class="demo-form-inline">
        <el-form-item>
          <el-select
            v-model="form.device"
            placeholder="请选择设备"
            clearable
            style="width: 270px"
          >
            // for loop devices
            <el-option
              v-for="item in devices"
              :key="item.device"
              :label="item.device"
              :value="item.device"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-date-picker
            v-model="form.historyAlarmTimeRange"
            type="datetimerange"
            :shortcuts="shortcuts"
            range-separator="To"
            start-placeholder="Start date"
            end-placeholder="End date"
          />
        </el-form-item>
      </el-form>
      <div>
        <el-button type="primary" @click="setAlarmData">更新数据</el-button>
        <TrainAllButton :data="devices" :fusion="true" @set-data="setData" />
      </div>
    </div>

    <div class="device-box">
      <WindTurbine
        v-for="item in devices"
        :key="item.device"
        :id="item.device"
        :status="item.status"
        :path="item.device"
        @click="handleViewDetail(item.device)"
      ></WindTurbine>
    </div>
  </el-row>

  <h1>异常预警一览表</h1>
  <el-table
    :data="alarmMessages"
    :row-class-name="tableRowClassName"
    style="width: 100%; margin-right: 25px"
  >
    <el-table-column prop="device" label="设备" align="center" />
    <el-table-column prop="time" label="时间" align="center" />
    <el-table-column prop="model_name" label="模型名称" align="center" />
    <el-table-column prop="status" label="状态" align="center" width="120" />
    <el-table-column prop="message" label="诊断信息" width="950">
      <template #default="{ row }">
        <div v-html="formatText(row.message)"></div>
      </template>
    </el-table-column>
  </el-table>

  <!-- 设备详情弹窗 -->
  <el-dialog
    v-model="deviceDetailDialogVisible"
    title="设备详情"
    width="80%"
    style="height: 80vh; overflow-y: auto"
  >
    <el-table :data="deviceDetail" style="width: 100%">
      <el-table-column prop="predict_time" label="预测时间" align="center" />
      <el-table-column prop="status" label="状态" align="center" width="120" />
      <el-table-column prop="message" label="诊断信息" width="950">
        <template #default="{ row }">
          <div v-html="formatText(row.message)"></div>
        </template>
      </el-table-column>
    </el-table>
  </el-dialog>
</template>

<style scoped>
.box {
  width: 100%;
  height: 100%;
  display: flex;
  flex-wrap: wrap;
}

.train-all {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  margin-right: 15px;
  justify-content: space-between;
}
.device-box {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 15px;
  margin-right: 15px;
}

h1 {
  font-size: 20px;
  margin-bottom: 20px;
}

.success-row {
  background-color: #f0f9eb; /* 浅绿色 */
}

.error-row {
  background-color: #f56c6c; /* 浅红色 */
}

.warning-row {
  background-color: #fdf6ec; /* 浅黄色 */
}
</style>
