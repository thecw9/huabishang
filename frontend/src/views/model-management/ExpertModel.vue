<script setup>
import { ref, reactive, watch, onMounted, onBeforeUnmount } from "vue";
import {
  getExpertModelInfo,
  getExpertModelDetailByKey,
} from "@/api/expertModel";
import { ElNotification, ElMessage } from "element-plus";
import {
  trimNumber,
  tableRowClassName,
  alarmCodeToStatus,
  formatText,
} from "@/utils/index";
import TrainAllButton from "@/components/TrainAllButton.vue";
import * as echarts from "echarts";

const data = ref([]);
const form = reactive({
  include: "",
  exclude: "",
});

const modelReportDialogVisible = ref(false);
const modelReportDialogData = reactive({
  report_path: "",
});

const setData = async () => {
  await getExpertModelInfo(
    form.include.replace(" ", "&"),
    form.exclude.replace(" ", "&"),
  ).then((res) => {
    if (res.code === 200) {
      console.log(res.data);
      data.value = res.data.map((item) => {
        return {
          key: item.key,
          path: item.path,
          device: item.device,
          status: alarmCodeToStatus(item.status),
          message: item.message,
          model_name: item.model_name,
          model_type: item.model_type,
          report_path: item.report_path,
          last_predict_time: item.last_predict_time
            ?.replace("T", " ")
            .split(".")[0],
        };
      });
      ElNotification({
        title: "查询成功",
        message: "数据查询成功",
        type: "success",
      });
    }
  });
};

const handleViewModelReport = async (key) => {
  const res = await getExpertModelDetailByKey(key);
  console.log(res);
  if (res.code === 200) {
    modelReportDialogData.report_path =
      "/minio-api/power-prophet/" + res.data[0].report_path;
    console.log(modelReportDialogData.report_path);
    modelReportDialogVisible.value = true;
  }
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
        <el-button type="primary" @click="setData">更新数据</el-button>
        <TrainAllButton :data="data" :set-data="setData" />
      </el-form-item>
    </el-form>
  </div>

  <!-- 数据展示 -->
  <h1 style="text-align: center; font-size: 24px; font-weight: 600">
    {{ form.include }}模型预警
  </h1>
  <el-table
    :data="data"
    border
    style="width: 100%"
    :row-class-name="tableRowClassName"
  >
    <el-table-column v-if="false" prop="key" label="编号" align="center" sortable />
    <el-table-column prop="device" label="设备" align="center" sortable />
    <el-table-column
      prop="model_name"
      label="模型名称"
      align="center"
      sortable
      width="280"
    />
    <el-table-column prop="status" label="状态" align="center" width="150" />
    <el-table-column prop="message" label="诊断信息" width="580">
      <template #default="{ row }">
        <div v-html="formatText(row.message)"></div>
      </template>
    </el-table-column>
    <el-table-column
      prop="last_predict_time"
      label="最后预测时间"
      align="center"
      width="180"
    />
    <el-table-column label="操作" align="center" width="160">
      <template #default="scope">
        <el-button @click="handleViewModelReport(scope.row.key)"
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
</template>

<style scoped lang="scss">
.input_box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.el-input {
  width: 300px;
  margin-right: 15px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 5px;
}

.el-select {
  width: 300px;
}

span {
  display: flex;
  font-size: 16px;
}
</style>
