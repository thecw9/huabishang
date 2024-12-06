<script setup>
import { ref, reactive, watch } from "vue";
import * as echarts from "echarts";
import { getHistoryDataByTime } from "@/api/measures";
import { ElNotification, ElMessage } from "element-plus";
import { trimNumber } from "@/utils";

const emit = defineEmits(["setComparisonData"]);

const key_store = ref("");
const name_store = ref("");
const unit_store = ref("");
// const threshold = ref(0.5);

const historyDataDrawer = ref(false);
const historyDataDrawerData = reactive({
  data: [],
  difference: [],
  status: [],
});
const historyDataTimeRange = ref([
  new Date(new Date().getTime() - 3600 * 1000 * 24 * 1),
  new Date(),
]);
const shortcuts = [
  {
    text: "当天数据",
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
    text: "日对比",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24);
      return [start, end];
    },
  },
  {
    text: "周对比",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
      return [start, end];
    },
  },
  {
    text: "月对比",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
      return [start, end];
    },
  },
  // {
  //   text: "过去三个月",
  //   value: () => {
  //     const end = new Date();
  //     const start = new Date();
  //     start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
  //     return [start, end];
  //   },
  // },
];

const historyDataChart = ref();
let historyDataChartInstance = null;

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

const handleOpenHistoryDataDrawer = () => {
  historyDataChartInstance = echarts.init(historyDataChart.value);
  window.addEventListener("resize", () => {
    historyDataChartInstance.resize();
  });
};

const handleCloseHistoryDataDrawer = () => {
  historyDataChartInstance.dispose();
};

const handleViewHistoryDataDrawer = async (key, path, unit) => {
  historyDataDrawer.value = true;
  key_store.value = key;
  name_store.value = path;
  unit_store.value = unit;
  setHistoryData();
};

const tableRowClassName = ({ row, rowIndex }) => {
  if (row.status === "正常") {
    return "success-row";
  } else if (row.status === "预警") {
    return "error-row";
  }
  return "warning-row";
};

const setHistoryData = async () => {
  const res = await getHistoryDataByTime(
    key_store.value,
    historyDataTimeRange.value[0],
    historyDataTimeRange.value[1]
  );
  if (res.code === 200) {
    // console.log("res data:", res.data);
    const historyData = res.data
      .map((item) => {
        return {
          time: item.service_time?.replace("T", " ").split(".")[0],
          value: trimNumber(item.value),
        };
      })
      .sort((a, b) => {
        return new Date(a.time) - new Date(b.time);
      });
    // table data setoption
    // 表格 差值计算
    // 初始化一个空数组来存储差值
    const differences = ["-"];
    // 遍历数组，从第二个元素开始（因为第一个元素前面没有元素来计算差值）
    for (let i = 1; i < historyData.length; i++) {
      // 计算当前元素与前一个元素的value差值
      const item_a = parseFloat(historyData[i].value);
      const item_b = parseFloat(historyData[i - 1].value);
      let diff;
      if (item_b == 0) {
        diff = trimNumber(item_a - item_b) + "%";
      } else {
        diff = trimNumber(100 * ((item_a - item_b) / item_b)) + "%";
      }
      // const diff = trimNumber(
      //   parseFloat(historyData[i].value) - parseFloat(historyData[i - 1].value)
      // );
      // 将差值添加到新数组中
      differences.push(diff);
    }
    // 表格 状态列
    // console.log("threshold:", threshold.value);
    let resultArray = []; // 创建一个空数组来存储判断结果
    differences.forEach(function (item) {
      const num = parseFloat(item); // 将字符串转换为数字
      let result; // 用于存储每个元素的判断结果
      // if (isNaN(num)) {
      //   // console.log("非数字值，无法判断");
      //   result = "-";
      // } else if (Math.abs(num) > threshold.value) {
      //   result = "预警";
      // } else {
      //   result = "正常";
      // }

      if (isNaN(num)) {
        result = "非数值，无法判断";
      } else if (Math.abs(num) > 10) {
        result = "注意";
      } else if (Math.abs(num) > 20) {
        result = "异常";
      } else if (Math.abs(num) > 30) {
        result = "严重异常";
      } else {
        result = "正常";
      }
      // 将判断结果添加到新数组中
      resultArray.push(result);
    });
    // 移除第一个元素
    resultArray.shift();
    differences.shift();
    historyData.shift();
    historyDataDrawerData.status = resultArray;
    historyDataDrawerData.difference = differences;
    // 表格 数值设置
    historyDataDrawerData.data = historyData;
    // 确保表格行数一致
    for (
      let i = 0;
      i <
      Math.min(
        historyDataDrawerData.data.length,
        historyDataDrawerData.difference.length
      );
      i++
    ) {
      historyDataDrawerData.data[i].difference =
        historyDataDrawerData.difference[i];
      historyDataDrawerData.data[i].unit = unit_store.value;
      historyDataDrawerData.data[i].status = historyDataDrawerData.status[i];
    }
    // chart setoption
    historyDataChartInstance.setOption({
      title: {
        text:
          props.title.replace("油色谱纵向对比数据", "") +
          `${name_store.value}历史数据`,
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

    ElNotification({
      title: "成功",
      message: "查询成功",
      type: "success",
    });
  } else {
    ElMessage.error("查询失败");
  }
};

// watch(
//   () => threshold.value,
//   () => {
//     setHistoryData();
//   },
//   { deep: true }
// );
</script>

<template>
  <div>
    <h1>{{ props.title }}</h1>
    <div class="table-box">
      <el-table :data="props.data" border style="width: 100%">
        <el-table-column prop="key" label="测点编号" align="center" />
        <el-table-column prop="path" label="测点" align="center" />
        <el-table-column prop="time" label="时间" align="center" />
        <el-table-column prop="value" label="值" align="center" width="140" />
        <el-table-column prop="unit" label="单位" align="center" width="100" />
        <el-table-column label="操作" align="center" fixed="right" width="320">
          <template #default="scope">
            <el-button
              @click="
                handleViewHistoryDataDrawer(
                  scope.row.key,
                  scope.row.path,
                  scope.row.unit
                )
              "
              >不同时间跨度纵向对比详情</el-button
            >
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 不同时间跨度对比详情抽屉 -->
    <el-drawer
      v-model="historyDataDrawer"
      title="不同时间跨度纵向对比详情"
      size="90%"
      @open="handleOpenHistoryDataDrawer"
      @closed="handleCloseHistoryDataDrawer"
    >
      <el-date-picker
        v-model="historyDataTimeRange"
        type="datetimerange"
        :shortcuts="shortcuts"
        range-separator="To"
        start-placeholder="Start date"
        end-placeholder="End date"
      />
      <el-button @click="setHistoryData">查询</el-button>
      <el-divider></el-divider>
      <div ref="historyDataChart" style="width: 100%; height: 300px"></div>
      <!-- <div
        class="threshold"
        style="display: flex; justify-content: center; text-align: center"
      >
        <p style="margin-right: 10px">请输入阈值:</p>
        <input
          type="number"
          v-model.number="threshold"
          placeholder="请输入阈值"
        />
        <p style="margin-left: 10px">当前阈值: {{ threshold }}</p>
      </div> -->
      <el-table
        :data="historyDataDrawerData.data"
        :row-class-name="tableRowClassName"
        border
        style="width: 100%"
        height="650"
      >
        <el-table-column prop="time" label="时间" align="center" />
        <el-table-column prop="value" label="值" align="center" />
        <el-table-column
          prop="difference"
          label="与上一时刻相差程度"
          align="center"
        />
        <el-table-column prop="unit" label="单位" align="center" />
        <el-table-column prop="status" label="状态" align="center" />
      </el-table>
    </el-drawer>
  </div>
</template>

<style scoped>
span {
  display: flex;
  font-size: 16px;
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
