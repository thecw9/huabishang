<script setup>
import { ref, reactive, watch } from "vue";
import * as echarts from "echarts";
import { getMeasuresInfo, getHistoryDataByTime } from "@/api/measures";
import { ElNotification, ElMessage } from "element-plus";
import { trimNumber } from "@/utils";

const emit = defineEmits(["setComparisonData"]);
const props = defineProps({
  title: {
    type: String,
    default: "",
  },
  devicePhase: {
    type: String,
    default: "",
  },
  data: {
    type: Object,
    default: () => [],
  },
});

const device_legend = ["A相", "B相", "C相"];
const name_store = ref("");
const unit_store = ref("");
const key_store_A = ref("");
const key_store_B = ref("");
const key_store_C = ref("");
const chart_data_list = ref([]);
const chart_series = ref([]);
// const threshold = ref(3);
// #region historyDataDrawer table columns setoption
// 初始化一个空数组来存储结果
let columns = [
  {
    prop: "time",
    label: "日期",
    align: "center",
    // width: 180,
  },
];
// 定义一个函数来生成 value 和 difference 对象
function generatePair(index) {
  return [
    {
      prop: `${device_legend[index]}id`,
      label: `${device_legend[index]}编号`,
      align: "center",
    },
    {
      prop: `${device_legend[index]}value`,
      label: `${device_legend[index]}值`,
      align: "center",
    },
    // {
    //   prop: `${device_legend[index]}difference`,
    //   label: `${device_legend[index]}差值`,
    //   align: "center",
    // },
  ];
  // 创建一个包含 value 和 difference 的对象
  // return [
  //   { prop: `value${index + 1}`, label: `v${index + 1}`, align: "center" },
  //   {
  //     prop: `difference${index + 1}`,
  //     label: `v${index + 1}差值`,
  //     align: "center",
  //   },
  // ];
}
// 使用循环来生成12对 value 和 difference
for (let i = 0; i < 3; i++) {
  // 调用函数并将结果展平后添加到 result 数组中
  columns.push(...generatePair(i));
}
columns.push(
  ...[
    {
      prop: "max",
      label: "三相最大值",
      align: "center",
    },
    {
      prop: "min",
      label: "三相最小值",
      align: "center",
    },
    {
      prop: "diff",
      label: "最大最小差值",
      align: "center",
    },
    {
      prop: "share",
      label: "当前时刻最值差值与上一时刻相差程度",
      align: "center",
    },
    {
      prop: "unit",
      label: "单位",
      align: "center",
    },
    {
      prop: "status",
      label: "状态",
      align: "center",
    },
  ],
);
// #endregion

const historyDataDrawer = ref(false);
const historyDataDrawerTableData = reactive({
  data: [],
});
const historyDataDrawerTableDataA = reactive({
  data: [],
});
const historyDataDrawerTableDataB = reactive({
  data: [],
});
const historyDataDrawerTableDataC = reactive({
  data: [],
});
// const historyDataDrawerTableDataDiffAB = ref([]);
// const historyDataDrawerTableDataDiffBC = ref([]);
// const historyDataDrawerTableDataDiffAC = ref([]);
const historyDataDrawerTableDataMax = ref([]);
const historyDataDrawerTableDataMin = ref([]);
const historyDataDrawerTableDataDiff = ref([]);
const historyDataDrawerTableDataShare = ref([]);
const historyDataDrawerTableDataStatus = ref([]);

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
];

const historyDataChart = ref();
let historyDataChartInstance = null;

const tableRowClassName = ({ row, rowIndex }) => {
  if (row.status === "正常") {
    return "success-row";
  } else if (row.status === "预警") {
    return "error-row";
  }
  return "warning-row";
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

const handleViewHistoryDataDrawer = async (path, unit) => {
  historyDataDrawer.value = true;
  name_store.value = path;
  unit_store.value = unit;
  setHistoryData();
};

const getPhaseHistoryDataByTime = async (
  phase_name,
  key_store,
  historyDataTimeRangeStart,
  historyDataTimeRangeEnd,
) => {
  const res = await getHistoryDataByTime(
    key_store,
    historyDataTimeRangeStart,
    historyDataTimeRangeEnd,
  );
  if (res.code === 200) {
    // console.log("res data:", res.data);
    const historyData = res.data
      .map((item) => {
        return {
          key: item.key,
          time: item.service_time?.replace("T", " ").split(".")[0],
          value: trimNumber(item.value),
        };
      })
      .sort((a, b) => {
        return new Date(a.time) - new Date(b.time);
      });

    ElNotification({
      title: "成功",
      message: `${phase_name}查询成功`,
      type: "success",
    });
    return historyData;
  } else {
    ElMessage.error("查询历史数据失败");
  }
};

const findMinMaxAndDiffAtIndexes = (arrays) => {
  // 确保数组不为空且至少包含一个元素数组
  if (!arrays.length || !arrays.some((arr) => arr.length)) return null;
  // 找出所有数组中最短的长度
  const minLength = Math.min(...arrays.map((arr) => arr.length));
  // 创建一个数组来存储每个索引的最大值、最小值和差值
  let result = [];
  // 遍历索引
  for (let i = 0; i < minLength; i++) {
    // 提取每个数组在索引i的元素到一个新数组
    const values = arrays.map((arr) => arr[i]);
    // 使用扩展运算符找到最大值和最小值
    const max = Math.max(...values);
    const min = Math.min(...values);
    // 计算差值
    const diff = max - min;
    // 将结果存储到结果数组中
    result.push({ max, min, diff });
  }

  return result;
};

const sethistoryDataDrawerTableStatus = (table_share) => {
  let resultArray = []; // 创建一个空数组来存储判断结果
  table_share.forEach(function (item) {
    const num = parseFloat(item); // 将字符串转换为数字
    let result; // 用于存储每个元素的判断结果
    if (isNaN(num)) {
      // console.log("非数字值，无法判断");
      result = "非数值，无法判断";
    } else if (Math.abs(num) > 20) {
      result = "注意";
    } else if (Math.abs(num) > 30) {
      result = "异常";
    } else if (Math.abs(num) > 40) {
      result = "严重异常";
    } else {
      result = "正常";
    }
    // 将判断结果添加到新数组中
    resultArray.push(result);
  });

  return resultArray;
};

const setHistoryData = async () => {
  // 获取对比的三相key
  const include_info = `${props.devicePhase}&${name_store.value}`;
  // console.log("include info:", include_info);
  const exclude_info = "告警&增量&测量量&速率";
  await getMeasuresInfo(include_info, exclude_info).then((res) => {
    if (res.code === 200) {
      key_store_A.value = res.data.find((item) => item.path.includes("A")).key;
      key_store_B.value = res.data.find((item) => item.path.includes("B")).key;
      key_store_C.value = res.data.find((item) => item.path.includes("C")).key;
    } else {
      ElMessage.error("三相key值请求失败");
    }
  });
  // 获取三相value
  const phase_A_history_data = await getPhaseHistoryDataByTime(
    "A相",
    key_store_A.value,
    historyDataTimeRange.value[0],
    historyDataTimeRange.value[1],
  );
  const phase_B_history_data = await getPhaseHistoryDataByTime(
    "B相",
    key_store_B.value,
    historyDataTimeRange.value[0],
    historyDataTimeRange.value[1],
  );
  const phase_C_history_data = await getPhaseHistoryDataByTime(
    "C相",
    key_store_C.value,
    historyDataTimeRange.value[0],
    historyDataTimeRange.value[1],
  );
  // console.log("phase_a_history data:", phase_A_history_data);
  // table data setoption
  const phase_A_value = phase_A_history_data.map((obj) =>
    parseFloat(obj.value),
  );
  const phase_B_value = phase_B_history_data.map((obj) =>
    parseFloat(obj.value),
  );
  const phase_C_value = phase_C_history_data.map((obj) =>
    parseFloat(obj.value),
  );
  const max_min_diff = findMinMaxAndDiffAtIndexes([
    phase_A_value,
    phase_B_value,
    phase_C_value,
  ]);
  historyDataDrawerTableDataMax.value = max_min_diff.map((obj) => {
    return trimNumber(obj.max);
  });
  historyDataDrawerTableDataMin.value = max_min_diff.map((obj) => {
    return trimNumber(obj.min);
  });
  historyDataDrawerTableDataDiff.value = max_min_diff.map((obj) => {
    return trimNumber(obj.diff);
  });
  // 表格 差值占比计算
  // 初始化一个空数组来存储差值
  historyDataDrawerTableDataShare.value = ["-"];
  // 遍历数组，从第二个元素开始（因为第一个元素前面没有元素来计算差值）
  for (let i = 1; i < historyDataDrawerTableDataDiff.value.length; i++) {
    // 计算当前元素与前一个元素的value差值
    const item_a = parseFloat(historyDataDrawerTableDataDiff.value[i]);
    const item_b = parseFloat(historyDataDrawerTableDataDiff.value[i - 1]);
    let diff;
    if (item_b == 0) {
      // diff = "与上一时刻突变, 变化" + trimNumber(item_a - item_b);
      // } else if (item_a - item_b == 1) {
      //   diff = "与上一时刻无变化";
      diff = trimNumber(item_a - item_b) + "%";
    } else {
      diff = trimNumber(100 * ((item_a - item_b) / item_b)) + "%";
    }
    // 将差值添加到新数组中
    historyDataDrawerTableDataShare.value.push(diff);
  }
  // table status
  historyDataDrawerTableDataStatus.value = sethistoryDataDrawerTableStatus(
    historyDataDrawerTableDataShare.value,
  );
  // 移除第一个元素
  phase_A_history_data.shift();
  phase_B_history_data.shift();
  phase_C_history_data.shift();
  historyDataDrawerTableDataMax.value.shift();
  historyDataDrawerTableDataMin.value.shift();
  historyDataDrawerTableDataDiff.value.shift();
  historyDataDrawerTableDataShare.value.shift();
  historyDataDrawerTableDataStatus.value.shift();
  // set columns option
  historyDataDrawerTableDataA.data = phase_A_history_data;
  historyDataDrawerTableDataB.data = phase_B_history_data;
  historyDataDrawerTableDataC.data = phase_C_history_data;
  historyDataDrawerTableData.data = [];
  for (
    let i = 0;
    i <
    Math.min(
      historyDataDrawerTableDataA.data.length,
      historyDataDrawerTableDataB.data.length,
      historyDataDrawerTableDataC.data.length,
    );
    i++
  ) {
    historyDataDrawerTableData.data[i] = {
      time: historyDataDrawerTableDataA.data[i]["time"],
      A相id: historyDataDrawerTableDataA.data[i]["key"],
      A相value: historyDataDrawerTableDataA.data[i]["value"],
      B相id: historyDataDrawerTableDataB.data[i]["key"],
      B相value: historyDataDrawerTableDataB.data[i]["value"],
      C相id: historyDataDrawerTableDataC.data[i]["key"],
      C相value: historyDataDrawerTableDataC.data[i]["value"],
      max: historyDataDrawerTableDataMax.value[i],
      min: historyDataDrawerTableDataMin.value[i],
      diff: historyDataDrawerTableDataDiff.value[i],
      share: historyDataDrawerTableDataShare.value[i],
      unit: unit_store.value,
      status: historyDataDrawerTableDataStatus.value[i],
    };
  }

  // chart setoption
  chart_data_list.value = [
    phase_A_history_data,
    phase_B_history_data,
    phase_C_history_data,
  ];
  chart_series.value = chart_data_list.value.map(function (data, index) {
    return {
      name: device_legend[index], // 系列名称，可以根据需要设置
      type: "line", // 系列类型，这里是折线图
      data: data, // 数据点数组
    };
  });
  historyDataChartInstance.setOption({
    title: {
      text: `${props.devicePhase}${name_store.value}历史数据`,
      left: "center",
      top: "5%",
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
    legend: {
      data: device_legend,
      top: "15%",
      textStyle: {
        color: "#ccc",
        // fontSize: 16,
      },
    },
    xAxis: {
      type: "category",
      data: phase_A_history_data.map((item) => item.time),
      // data: ["类别1", "类别2", "类别3", "类别4", "类别5", "类别6", "类别7"],
    },
    yAxis: {
      type: "value",
      // min:
      //   Math.min(...historyData.map((item) => item.value)) -
      //   (Math.max(...historyData.map((item) => item.value)) -
      //     Math.min(...historyData.map((item) => item.value))) *
      //     0.2,
      // max:
      //   Math.max(...historyData.map((item) => item.value)) +
      //   (Math.max(...historyData.map((item) => item.value)) -
      //     Math.min(...historyData.map((item) => item.value))) *
      //     0.2,
      splitLine: {
        show: false,
      },
    },
    series: chart_series.value,
  });
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
                handleViewHistoryDataDrawer(scope.row.path, scope.row.unit)
              "
              >不同时间跨度横向对比详情</el-button
            >
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 不同时间跨度对比详情抽屉 -->
    <el-drawer
      v-model="historyDataDrawer"
      title="不同时间跨度横向对比详情"
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
        :data="historyDataDrawerTableData.data"
        :row-class-name="tableRowClassName"
        border
        style="width: 100%"
        height="650"
      >
        <el-table-column
          v-for="column in columns"
          :key="column.prop"
          :prop="column.prop"
          :label="column.label"
          :align="column.align"
        >
        </el-table-column>
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
