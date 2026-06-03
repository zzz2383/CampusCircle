import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import { ElMessage } from 'element-plus'

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
        { path: '/events/:id', name: 'eventDetail', component: () => import('@/views/EventDetail.vue') },
        { path: '/events', name: 'events', component: () => import('@/views/EventList.vue') },
        { path: '/admin', name: 'admin', component: () => import('@/views/AdminDashboard.vue') },
    ],
})

// 全局前置守卫：等待认证初始化完成
// 在已有的 router.beforeEach 中添加
router.beforeEach(async (to, _from) => {
    const userStore = useUserStore()
    await userStore.initAuth()

    if (to.path === '/admin') {
        if (!userStore.isLoggedIn) {
            return '/auth'           // 重定向到登录页
        }
        if (userStore.user?.role !== 'admin') {
            ElMessage.error('无权限访问管理后台')
            return '/'               // 重定向到首页
        }
        // 允许访问，不返回任何值或返回 true
        return true
    }
    // 其他路由直接放行
})
export default router