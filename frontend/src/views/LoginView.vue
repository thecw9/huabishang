<script setup>
import { login } from "@/api/auth";
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { ElNotification } from "element-plus";

const router = useRouter();

const loginForm = reactive({
  username: "",
  password: "",
  remember: false,
});

const rules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
};

const loginFormRef = ref(null);

const onSubmit = () => {
  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      await login(loginForm.username, loginForm.password).then((res) => {
        // 提示登录成功
        ElNotification({
          title: "Success",
          message: res.message,
          type: "success",
          duration: 2000,
        });

        // 保存token

        // 跳转到首页
        router.push({ path: "/index" });
      });
    } else {
      ElNotification({
        title: "Error",
        message: "用户名或密码不能为空",
        type: "error",
      });
    }
  });
};
</script>

<template>
  <div class="login-page">
    <div class="login-header"></div>

    <div class="login-panel">
      <h1 class="login-title">风电机组异常预警系统</h1>
      <el-form :rules="rules" ref="loginFormRef" :model="loginForm" label-width="0px">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" prefix-icon="User" @keyup.enter.native="onSubmit">
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input show-password type="password" v-model="loginForm.password" placeholder="请输入密码" prefix-icon="Lock"
            @keyup.enter.native="onSubmit">
          </el-input>
        </el-form-item>
        <el-checkbox class="remember-box opacity-50" v-model="loginForm.remember">记住密码</el-checkbox>
        <el-form-item>
          <el-button type="primary" class="login-btn" @click="onSubmit">登录</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="login-footer">
      <!-- 版权信息 -->
      <span>© 2023 长沙理工大学 版权所有</span>
      <span>技术支持：长沙理工大学</span>
      <span>地址：湖南省长沙市雨花区万家丽南路二段960号</span>
      <span>邮编：410114</span>
      <span>电话：0731-85251114</span>
      <span>传真：0731-85251114</span>
    </div>
  </div>
</template>

<style scoped lang="scss">
.login-page {
  .login-panel {
    width: 500px;
    background-color: #60a5fa60;
    padding: 20px;
    border-radius: 5px;

    .login-title {
      text-align: center;
      font-size: 24px;
      font-weight: 600;
      color: rgba(255, 255, 255, 0.6);
      margin-bottom: 20px;
    }

    .remember-box {
      color: rgba(255, 255, 255);
    }
  }

  .el-button {
    width: 100%;
    height: 40px;
    margin-top: 6px;
  }

  .login-footer {
    width: 100%;
    background-color: rgba(255, 255, 255, 0.1);
    padding: 20px;
    border-radius: 5px;
    color: rgba(255, 255, 255, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    @apply space-x-2;
  }
}
</style>
