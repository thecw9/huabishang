<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const onExit = () => {
  router.push({ path: '/login' })
}

const breadcrumb_list = ref([])

// 监听路由变化
watch(() => route.matched, () => {
  breadcrumb_list.value = route.matched
})

onMounted(() => {
  breadcrumb_list.value = route.matched
})

</script>

<template>
  <el-header class="header">
    <el-breadcrumb separator="/">
      <!-- <el-breadcrumb-item :to="{ path: '/' }">homepage</el-breadcrumb-item> -->
      <el-breadcrumb-item v-for="item in breadcrumb_list" :key="item.path" :to="{ path: item.path }"><span
          class="breadcrumb_text">
          {{ item.meta.title }}</span></el-breadcrumb-item>
    </el-breadcrumb>
    <el-button type="primary" class="exit-btn" @click="onExit">退出</el-button>
  </el-header>
</template>

<style scoped>
.header {
  width: 100%;
  height: 60px;
  background-color: #545c6410;
  @apply flex items-center;
}

.breadcrumb_text {
  color: #fff;

  &:hover {
    color: #409eff;
  }
}



.exit-btn {
  position: absolute;
  right: 20px;
}
</style>
