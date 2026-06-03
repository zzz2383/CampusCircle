import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/userStore'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', name: 'home', component: () => import('@/views/HomePage.vue') },
        { path: '/auth', name: 'auth', component: () => import('@/views/LoginRegister.vue') },
        { path: '/posts/:id', name: 'postDetail', component: () => import('@/views/PostDetail.vue') },
        { path: '/rank', name: 'rank', component: () => import('@/views/Rank.vue') },
        { path: '/profile', name: 'profile', component: () => import('@/views/Profile.vue') },
        { path: '/lost-items', name: 'lostItems', component: () => import('@/views/LostItem.vue') },
        { path: '/clubs/:id', name: 'clubDetail', component: () => import('@/views/ClubDetail.vue') },
        { path: '/clubs', name: 'clubs', component: () => import('@/views/ClubList.vue') },
    ],
})

// 全局前置守卫：等待认证初始化完成
router.beforeEach(async (_to, _from) => {
    const userStore = useUserStore()
    await userStore.initAuth()
    // 不返回任何值或返回 true 都表示允许导航
})

export default router