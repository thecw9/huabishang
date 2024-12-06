<script setup>
import { ref, reactive, onMounted, watch, onBeforeUnmount, provide } from "vue";
import { getMeasuresInfo } from "@/api/measures";
import { getSingleModelInfo } from "@/api/singleModel";
import { trimNumber, mergeArrays, alarmCodeToStatus } from "@/utils";
import DataTable from "@/components/DataTable.vue";
import TrainAllButton from "@/components/TrainAllButton.vue";

const data = ref([]);
const form = reactive({
  include: "#1号机组",
  exclude: "",
});

const setData = async () => {
  const model_info = await getSingleModelInfo(
    form.include.replace(" ", "&"),
    form.exclude,
  );
  const measure_data = await getMeasuresInfo(
    form.include.replace(" ", "&"),
    form.exclude,
  );
  const merged_data = mergeArrays(measure_data.data, model_info.data, "key");
  data.value = merged_data
    .map((item) => {
      return {
        key: item.key,
        // path: item.path.split("_")[item.path.split("_").length - 1],
        // path: item.path.split("/")[item.path.split("/").length - 1],
        path: item.path,
        time: item.time?.replace("T", " ").split(".")[0],
        value: trimNumber(item.value),
        unit: item.unit,
        status: alarmCodeToStatus(item.status),
        message: item.message?.split(" ")[item.message.split(" ").length - 1],
        report_path: item.report_path,
      };
    })
    // .filter((item) => {
    // return item.unit;
    // })
    .sort((a, b) => {
      return a.key.localeCompare(b.key);
    });
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
    <el-form :inline="true" :model="form" class="demo-form-inline">
      <el-form-item label="包含">
        <el-input
          v-model="form.include"
          placeholder="请输入include关键字"
        ></el-input>
      </el-form-item>
      <el-form-item label="排除">
        <el-input
          v-model="form.exclude"
          placeholder="请输入exclude关键字"
        ></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="setData">更新数据</el-button>
        <TrainAllButton :data="data" :set-data="setData" />
      </el-form-item>
    </el-form>
  </div>
  <!-- 数据展示 -->
  <DataTable
    :data="data"
    :title="`${form.include}在线监测评估`"
    @set-data="setData"
  />
</template>

<style scoped></style>
