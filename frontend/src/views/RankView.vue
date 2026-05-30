<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import type { PostDTO } from '../types/api'

const hotPosts = ref<PostDTO[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/rank/hot-posts?limit=10')
    hotPosts.value = res.data
  } catch (err) {
    console.error('Failed to load rank:', err)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="rank-view">
    <h1>今日热帖榜</h1>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="hotPosts.length === 0" class="empty">暂无数据</div>
    <div v-else class="rank-list">
      <div v-for="(post, index) in hotPosts" :key="post.id" class="rank-item">
        <span class="rank-number" :class="{ top3: index < 3 }">{{ index + 1 }}</span>
        <router-link :to="`/posts/${post.id}`" class="rank-title">
          {{ post.title }}
        </router-link>
        <span class="rank-score">{{ post.like_count }} 👍</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.rank-view {
  max-width: 600px;
  margin: 0 auto;
}

h1 {
  font-size: 24px;
  margin-bottom: 20px;
}

.loading,
.empty {
  text-align: center;
  padding: 40px;
  color: #999;
}

.rank-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rank-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.rank-number {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
  background: #f0f0f0;
  color: #666;
}

.rank-number.top3 {
  background: #ff4d4f;
  color: #fff;
}

.rank-title {
  flex: 1;
  text-decoration: none;
  color: #333;
  font-size: 14px;
}

.rank-title:hover {
  color: #1677ff;
}

.rank-score {
  font-size: 12px;
  color: #999;
}
</style>
