<script setup>
import { computed } from "vue";

const props = defineProps({
  path: { type: String, default: "" },
  status: { type: String, default: "" },
});

const className = computed(() => ({
  "normal-element": props.status === "正常",
  "watch-element": props.status === "注意",
  "warning-element": props.status === "警告",
  "critical-element": props.status === "严重",
  "emergency-element": props.status === "紧急",
  "unknown-element": props.status === "-1",
}));
</script>

<template>
  <div class="wind-turbine" :class="className">
    <p class="id">{{ path }}</p>
    <div class="fan-head">
      <div class="wheel"></div>
      <div class="blade blade1"></div>
      <div class="blade blade2"></div>
      <div class="blade blade3"></div>
    </div>
    <div class="tower"></div>
    <p class="status">状态: {{ status }}</p>
  </div>
</template>

<style scoped>
.wind-turbine {
  width: 150px;
  height: 205px;
  border: 2px solid #73e2de70;
  margin: 4px 5px;
  position: relative;
}

.normal {
  background-color: #409eff20;

  .fan-head {
    /* 主要代码：实现旋转的动画 */
    animation: rotate 3s linear infinite;
  }
}

.alarm {
  background-color: rgba(255, 0, 0, 0.5);

  .prealarm {
    background-color: rgba(255, 255, 0, 0.5);
  }

  .fan-head {
    /* 主要代码：实现旋转的动画 */
    animation: rotate 3s linear infinite;
  }
}

.fan-head {
  /* 主要代码：实现旋转的动画 */
  animation: rotate 25s linear infinite;
}

.fan-head {
  width: 124px;
  height: 124px;
  position: absolute;
  top: 6px;
}

.wheel {
  width: 20px;
  height: 20px;
  background-color: #73e2de;
  border-radius: 50%;
  position: absolute;
  top: 52px;
  margin-left: 52px;
}

.tower {
  width: 15px;
  height: 90px;
  background: #73e2de;
  clip-path: polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%);
  position: absolute;
  top: 70px;
  margin-left: 54px;
}

.blade {
  width: 12px;
  height: 50px;
  background: #73e2de;
  transform-origin: right bottom;
  position: fixed;
  border-top-left-radius: 45%;
  border-top-right-radius: 45%;
  border-bottom-left-radius: 45%;
  border-bottom-right-radius: 45%;
}

.blade1 {
  position: absolute;
  margin-left: 56px;
  margin-top: 1px;
  transform: rotate(0deg);
}

.blade2 {
  position: absolute;
  margin-left: 57px;
  margin-top: 22px;
  transform: rotate(120deg);
}

.blade3 {
  position: absolute;
  margin-left: 37px;
  margin-top: 12px;
  transform: rotate(240deg);
}

.status {
  height: 5px;
  position: absolute;
  margin-left: 3px;
  bottom: 15px;
}

.id {
  margin-left: 3px;
}

@keyframes rotate {
  0% {
    -webkit-transform: rotate(0deg);
  }

  25% {
    -webkit-transform: rotate(90deg);
  }

  50% {
    -webkit-transform: rotate(180deg);
  }

  75% {
    -webkit-transform: rotate(270deg);
  }

  100% {
    -webkit-transform: rotate(360deg);
  }
}
</style>
