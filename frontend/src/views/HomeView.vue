<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { postService } from '../services/postService'
import type { PostDTO } from '../types/api'

const posts = ref<PostDTO[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await postService.list(0, 20)
    posts.value = res.items
  } catch (err) {
    console.error('Failed to load posts:', err)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="home-view">
    <h1>最新帖子</h1>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="posts.length === 0" class="empty">暂无帖子</div>
    <div v-else class="post-list">
      <div v-for="post in posts" :key="post.id" class="post-card">
        <router-link :to="`/posts/${post.id}`" class="post-title">
          {{ post.title }}
        </router-link>
        <p class="post-meta">
          <span>{{ post.author_nickname || '匿名' }}</span>
          <span>❤️ {{ post.like_count }}</span>
          <span>💬 {{ post.comment_count }}</span>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-view {
  max-width: 800px;
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

.post-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-card {
  background: #fff;
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.post-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  text-decoration: none;
  display: block;
  margin-bottom: 8px;
}

.post-title:hover {
  color: #1677ff;
}

.post-meta {
  font-size: 12px;
  color: #999;
  display: flex;
  gap: 16px;
}
</style>
