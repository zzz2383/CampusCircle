<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/authService'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const student_id = ref('')
const password = ref('')
const errorMsg = ref('')

async function handleLogin() {
  try {
    const result = await authService.login({
      student_id: student_id.value,
      password: password.value,
    })
    authStore.setAuth(result)
    router.push('/')
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || '登录失败'
  }
}
</script>

<template>
  <div class="login-view">
    <div class="login-card">
      <h2>登录</h2>
      <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>学号/工号</label>
          <input v-model="student_id" type="text" placeholder="请输入学号" required />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="请输入密码" required />
        </div>
        <button type="submit" class="btn-submit">登录</button>
      </form>
      <p class="register-link">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.login-view {
  display: flex;
  justify-content: center;
  padding-top: 60px;
}

.login-card {
  background: #fff;
  padding: 32px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  width: 360px;
}

h2 {
  text-align: center;
  margin-bottom: 24px;
}

.error {
  color: #ff4d4f;
  text-align: center;
  margin-bottom: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 14px;
  margin-bottom: 4px;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.btn-submit {
  width: 100%;
  padding: 10px;
  background: #1677ff;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

.btn-submit:hover {
  background: #4096ff;
}

.register-link {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
}
</style>
