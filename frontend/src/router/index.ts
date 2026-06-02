import { createRouter, createWebHistory } from 'vue-router'
import LoginRegister from '@/views/auth/LoginRegister.vue'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            redirect: '/auth',
        },
        {
            path: '/auth',
            name: 'auth',
            component: LoginRegister,
        },
        // 后续其他页面...
    ],
})

export default router