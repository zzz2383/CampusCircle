<template>
  <router-view />
</template>

<script setup lang="ts">
import { useUserStore } from './stores/userStore'
import { onMounted } from 'vue'

const userStore = useUserStore()

onMounted(() => {
  userStore.initAuth()
})
</script>