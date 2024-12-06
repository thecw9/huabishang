<script setup>
</script>

<template>
  <div class="notfound-page">
    <el-result icon="warning" title="页面未找到" sub-title="你找到页面不存在">
      <template #extra>
        <el-button type="primary" @click="$router.push('/home')">返回主页</el-button>
      </template>
    </el-result>
  </div>
</template>

<style scoped>
.notfound-page {
  background-image: url('@/assets/404.png');
  height: 100vh;
}
</style>
