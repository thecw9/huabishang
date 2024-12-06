<script setup>
import Aside from "@/components/Aside.vue";
import Header from "@/components/Header.vue";
</script>

<template>
  <div class="home-page">
    <el-container>
      <Aside />
      <el-container>
        <el-header>
          <Header />
        </el-header>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped></style>
