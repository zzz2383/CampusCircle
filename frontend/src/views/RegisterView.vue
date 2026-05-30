<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/authService'

const router = useRouter()

const form = ref({
  student_id: '',
  email: '',
  password: '',
  nickname: '',
})
const errorMsg = ref('')

async function handleRegister() {
  try {
    await authService.register(form.value)
    router.push('/login')
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || '注册失败'
  }
}
</script>

<template>
  <div class="register-view">
    <div class="register-card">
      <h2>注册</h2>
      <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label>学号/工号</label>
          <input v-model="form.student_id" type="text" placeholder="请输入学号" required />
        </div>
        <div class="form-group">
          <label>校园邮箱</label>
          <input v-model="form.email" type="email" placeholder="xxx@campus.edu" required />
        </div>
        <div class="form-group">
          <label>昵称</label>
          <input v-model="form.nickname" type="text" placeholder="请输入昵称" required />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="form.password" type="password" placeholder="至少6位密码" required />
        </div>
        <button type="submit" class="btn-submit">注册</button>
      </form>
      <p class="login-link">
        已有账号？<router-link to="/login">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.register-view {
  display: flex;
  justify-content: center;
  padding-top: 60px;
}

.register-card {
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

.login-link {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
}
</style>
