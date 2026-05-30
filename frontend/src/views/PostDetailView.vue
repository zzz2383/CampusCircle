<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { postService } from '../services/postService'
import { likeService } from '../services/likeService'
import type { PostDTO } from '../types/api'

const route = useRoute()
const post = ref<PostDTO | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const id = Number(route.params.id)
    post.value = await postService.getById(id)
  } catch (err) {
    console.error('Failed to load post:', err)
  } finally {
    loading.value = false
  }
})

async function toggleLike() {
  if (!post.value) return
  try {
    if (post.value.is_liked) {
      post.value = { ...post.value, ...(await likeService.unlike(post.value.id)) }
    } else {
      post.value = { ...post.value, ...(await likeService.like(post.value.id)) }
    }
  } catch (err) {
    console.error('Like failed:', err)
  }
}
</script>

<template>
  <div class="post-detail">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="post" class="post-card">
      <h1>{{ post.title }}</h1>
      <div class="meta">
        <span>{{ post.author_nickname || '匿名' }}</span>
        <span>{{ post.created_at }}</span>
        <span v-if="post.tags">🏷️ {{ post.tags }}</span>
      </div>
      <div class="content">{{ post.content }}</div>
      <div class="actions">
        <button class="btn-like" :class="{ liked: post.is_liked }" @click="toggleLike">
          {{ post.is_liked ? '❤️' : '🤍' }} {{ post.like_count }}
        </button>
      </div>
    </div>
    <div v-else class="empty">帖子不存在</div>
  </div>
</template>

<style scoped>
.post-detail {
  max-width: 800px;
  margin: 0 auto;
}

.loading,
.empty {
  text-align: center;
  padding: 40px;
  color: #999;
}

.post-card {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

h1 {
  font-size: 24px;
  margin-bottom: 12px;
}

.meta {
  font-size: 12px;
  color: #999;
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.content {
  font-size: 15px;
  line-height: 1.8;
  color: #333;
  margin-bottom: 24px;
  white-space: pre-wrap;
}

.actions {
  display: flex;
  gap: 12px;
}

.btn-like {
  padding: 6px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
}

.btn-like.liked {
  color: #ff4d4f;
  border-color: #ff4d4f;
}
</style>
