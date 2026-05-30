<script setup lang="ts">
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="app-layout">
    <header class="app-header">
      <div class="header-content">
        <router-link to="/" class="logo">校园圈</router-link>
        <nav class="nav-links">
          <router-link to="/">首页</router-link>
          <router-link to="/rank">排行榜</router-link>
        </nav>
        <div class="user-area">
          <template v-if="authStore.isLoggedIn()">
            <span class="username">{{ authStore.currentUser?.nickname }}</span>
            <button class="btn-logout" @click="handleLogout">退出</button>
          </template>
          <template v-else>
            <router-link to="/login" class="btn-login">登录</router-link>
            <router-link to="/register" class="btn-register">注册</router-link>
          </template>
        </div>
      </div>
    </header>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: #f5f5f5;
}

.app-header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
  height: 56px;
  display: flex;
  align-items: center;
  gap: 24px;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  color: #1677ff;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 16px;
  flex: 1;
}

.nav-links a {
  color: #333;
  text-decoration: none;
  font-size: 14px;
}

.nav-links a:hover {
  color: #1677ff;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  font-size: 14px;
  color: #333;
}

.btn-login,
.btn-register,
.btn-logout {
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  text-decoration: none;
}

.btn-login {
  color: #1677ff;
  border: 1px solid #1677ff;
  background: #fff;
}

.btn-register {
  color: #fff;
  background: #1677ff;
  border: 1px solid #1677ff;
}

.btn-logout {
  color: #666;
  border: 1px solid #d9d9d9;
  background: #fff;
}

.main-content {
  max-width: 1200px;
  margin: 24px auto;
  padding: 0 16px;
}
</style>
