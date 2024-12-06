<script setup>
import { ref, reactive, watch, onMounted } from "vue";
import axios from "axios";
import Papa from "papaparse";
import { getTestModelInfo, predictTestModel } from "@/api/testModel";
import { ElNotification, ElMessage } from "element-plus";
import { trimNumber } from "@/utils/index";
import TrainAllButton from "@/components/TrainAllButton.vue";

const data = ref([]);
const form = reactive({
  include: "",
  exclude: "",
});

const headers = ref([]);
const rows = ref([]);

const modelReportDialogVisible = ref(false);

const setData = async () => {
  await getTestModelInfo(
    form.include.replace(" ", "&"),
    form.exclude.replace(" ", "&"),
  ).then((res) => {
    if (res.code === 200) {
      console.log(res.data);
      data.value = res.data.map((item) => {
        return {
          name: item.name,
          description: item.description,
          data_path: item.data_path,
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

const handleViewModelReport = async (data_path) => {
  modelReportDialogVisible.value = true;
  axios.get("/minio-api/power-prophet/" + data_path).then((res) => {
    Papa.parse(res.data, {
      header: true,
      complete: (result) => {
        headers.value = result.meta.fields;
        rows.value = result.data;
      },
      header: true,
    });
  });
};

const handleDownloadData = async (data_path) => {
  axios({
    method: "get",
    url: "/minio-api/power-prophet/" + data_path,
    responseType: "blob",
  }).then((res) => {
    const link = document.createElement("a");
    const blob = new Blob([res.data]);
    link.style.display = "none";
    link.href = URL.createObjectURL(blob);
    link.download = data_path;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  });
};

const handlePredict = async (name) => {
  ElNotification({
    title: "预测中",
    message: "预测中",
    type: "info",
    duration: 30000, // 30s后自动关闭
  });

  await predictTestModel(name).then((res) => {
    if (res.code === 200) {
      ElNotification({
        title: "预测成功",
        message: "预测成功",
        type: "success",
        duration: 30000, // 30s后自动关闭
      });
    }
  });
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
    {{ form.include }}模型测试
  </h1>
  <el-table :data="data" border style="width: 100%">
    <el-table-column prop="name" label="名称" align="center" width="180" />
    <el-table-column prop="description" label="描述">
      <template #default="{ row }">
        <div v-html="row.description"></div>
      </template>
    </el-table-column>
    <el-table-column
      prop="data_path"
      label="数据路径"
      align="center"
      width="280"
    />
    <el-table-column label="操作" align="center" width="290">
      <template #default="scope">
        <el-button @click="handleViewModelReport(scope.row.data_path)"
          >查看数据</el-button
        >
        <el-button @click="handleDownloadData(scope.row.data_path)"
          >下载数据</el-button
        >
        <el-button @click="handlePredict(scope.row.name)">预测</el-button>
      </template>
    </el-table-column>
  </el-table>

  <!-- 故障数据弹窗 -->
  <el-dialog
    v-model="modelReportDialogVisible"
    modal="false"
    width="80%"
    align-center="true"
    show-close="false"
  >
    <el-table
      :data="rows"
      style="width: 100%; margin-top: 0px"
      border
      height="900"
    >
      <el-table-column
        v-for="header in headers"
        :key="header"
        :prop="header"
        :label="header"
        align="center"
      >
      </el-table-column>
    </el-table>
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
  font-size: 26px;
}
</style>
