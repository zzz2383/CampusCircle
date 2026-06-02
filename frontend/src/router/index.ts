import { createRouter, createWebHistory } from 'vue-router'
import LoginRegister from '@/views/auth/LoginRegister.vue'
import HomePage from '@/views/HomePage.vue'
import PostDetail from '@/views/PostDetail.vue'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomePage,
        },
        {
            path: '/auth',
            name: 'auth',
            component: LoginRegister,
        },
        {
            path: '/posts/:id',
            name: 'postDetail',
            component: PostDetail,
        },
    ],
})

// 路由守卫：未登录可访问首页，但发帖等操作在组件内拦截
export default router