import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/userStore'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', name: 'home', component: () => import('@/views/HomePage.vue') },
        { path: '/auth', name: 'auth', component: () => import('@/views/auth/LoginRegister.vue') },
        { path: '/posts/:id', name: 'postDetail', component: () => import('@/views/PostDetail.vue') },
        { path: '/rank', name: 'rank', component: () => import('@/views/Rank.vue') },
        { path: '/profile', name: 'profile', component: () => import('@/views/Profile.vue') },
    ],
})

// 全局前置守卫：等待认证初始化完成
router.beforeEach(async (_to, _from, next) => {
    const userStore = useUserStore()
    // 如果还没有初始化过，等待 initAuth 完成
    await userStore.initAuth()
    next()
})

export default router