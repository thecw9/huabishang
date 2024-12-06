<script setup>
import { ref, reactive, onMounted, watch, onBeforeUnmount, provide } from "vue";
import { getMeasuresInfo } from "@/api/measures";
import { getSingleModelInfo } from "@/api/singleModel";
import { trimNumber, mergeArrays, alarmCodeToStatus } from "@/utils";
import DataTable from "@/components/DataTable.vue";
import TrainAllButton from "@/components/TrainAllButton.vue";

const data = ref([]);
const form = reactive({
  plant: "画笔山风电场",
  unit: "#1号机组",
});

const setData = async () => {
  const measure_data = await getMeasuresInfo(
    form.plant + "&" + form.unit + "&" + "默认变量",
  );
  const model_info = await getSingleModelInfo(
    form.plant + "&" + form.unit + "&" + "默认变量",
  );
  const merged_data = mergeArrays(measure_data.data, model_info.data, "key");
  data.value = merged_data
    .map((item) => {
      return {
        key: item.key,
        // path: item.path.split("_")[item.path.split("_").length - 1],
        path: item.path.split("/")[item.path.split("/").length - 1],
        time: item.time?.replace("T", " ").split(".")[0],
        value: trimNumber(item.value),
        unit: item.unit,
        status: alarmCodeToStatus(item.status),
        message: item.message?.split(" ")[item.message.split(" ").length - 1],
        report_path: item.report_path,
      };
    })
    .sort((a, b) => {
      return a.key.localeCompare(b.key);
    });
  console.log(data.value);
};

watch(
  () => form,
  () => {
    setData();
  },
  { deep: true },
);

let interval = null;
onMounted(() => {
  setData();
  interval = setInterval(() => {
    setData();
  }, 10000);
});

onBeforeUnmount(() => {
  clearInterval(interval);
});
</script>

<template>
  <!-- 搜索框 -->
  <div class="input_box">
    <el-form :inline="true" :model="form">
      <el-form-item label="设备">
        <el-select
          v-model="form.plant"
          placeholder="请选择电厂"
          clearable
          style="width: 270px"
        >
          <el-option label="画笔山风电场" value="画笔山风电场" />
        </el-select>
      </el-form-item>
      <el-form-item label="相位">
        <el-select
          v-model="form.unit"
          placeholder="请选择机组"
          clearable
          style="width: 270px"
        >
          <el-option label="#1号机组" value="#1号机组" />
          <el-option label="#2号机组" value="#2号机组" />
          <el-option label="#3号机组" value="#3号机组" />
          <el-option label="#4号机组" value="#4号机组" />
          <el-option label="#5号机组" value="#5号机组" />
          <el-option label="#6号机组" value="#6号机组" />
          <el-option label="#7号机组" value="#7号机组" />
          <el-option label="#8号机组" value="#8号机组" />
          <el-option label="#9号机组" value="#9号机组" />
          <el-option label="#10号机组" value="#10号机组" />
          <el-option label="#11号机组" value="#11号机组" />
          <el-option label="#12号机组" value="#12号机组" />
          <el-option label="#13号机组" value="#13号机组" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="setData">更新数据</el-button>
        <TrainAllButton :data="data" @set-data="setData" />
      </el-form-item>
    </el-form>
  </div>
  <!-- 数据展示 -->
  <DataTable
    :title="`${form.plant}${form.unit}油色谱在线监测评估`"
    :data="data"
    @set-data="setData"
  />
</template>

<style scoped></style>
