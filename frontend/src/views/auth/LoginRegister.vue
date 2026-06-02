<template>
    <div class="auth-container">
        <div class="decor-dot dot1"></div>
        <div class="decor-dot dot2"></div>

        <div class="auth-card">
            <div class="brand">
                <h1>CampusCircle</h1>
                <div class="sub">校园圈 · 连接真实校园</div>
            </div>

            <el-tabs v-model="activeTab" @tab-click="handleTabClick" stretch>
                <el-tab-pane label="登录" name="login">
                    <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-position="top"
                        size="large">
                        <el-form-item label="学号 / 工号" prop="student_id">
                            <el-input v-model="loginForm.student_id" placeholder="例如 202411001" clearable />
                        </el-form-item>
                        <el-form-item label="密码" prop="password">
                            <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password />
                        </el-form-item>
                        <div class="extra-links">
                            <a href="javascript:void(0)" @click="simulateForget">忘记密码?</a>
                        </div>
                        <el-form-item>
                            <el-button type="primary" @click="handleLogin" :loading="loginLoading" style="width: 100%">
                                登 录
                            </el-button>
                        </el-form-item>
                    </el-form>
                    <div class="demo-hint">测试学号：20240001 / 密码：123456</div>
                </el-tab-pane>

                <el-tab-pane label="注册" name="register">
                    <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" label-position="top"
                        size="large">
                        <el-form-item label="学号 / 工号" prop="student_id">
                            <el-input v-model="registerForm.student_id" placeholder="例如 202411001" clearable />
                        </el-form-item>
                        <el-form-item label="校园邮箱" prop="email">
                            <el-input v-model="registerForm.email" placeholder="stu@edu.cn / 学校邮箱" clearable />
                        </el-form-item>
                        <el-form-item label="昵称 (选填)" prop="nickname">
                            <el-input v-model="registerForm.nickname" placeholder="同学, 给自己一个有趣的称呼" clearable />
                        </el-form-item>
                        <div class="form-row">
                            <el-form-item label="院系" prop="department">
                                <el-select v-model="registerForm.department" placeholder="选择院系" clearable
                                    style="width: 100%">
                                    <el-option label="计算机学院" value="计算机学院" />
                                    <el-option label="软件学院" value="软件学院" />
                                    <el-option label="信息工程学院" value="信息工程学院" />
                                    <el-option label="经济管理学院" value="经济管理学院" />
                                    <el-option label="人文学院" value="人文学院" />
                                    <el-option label="其他" value="其他" />
                                </el-select>
                            </el-form-item>
                            <el-form-item label="年级" prop="grade">
                                <el-select v-model="registerForm.grade" placeholder="年级" clearable style="width: 100%">
                                    <el-option label="2026级" value="2026级" />
                                    <el-option label="2025级" value="2025级" />
                                    <el-option label="2024级" value="2024级" />
                                    <el-option label="2023级" value="2023级" />
                                    <el-option label="研究生/教师" value="研究生/教师" />
                                </el-select>
                            </el-form-item>
                        </div>
                        <el-form-item label="密码" prop="password">
                            <el-input v-model="registerForm.password" type="password" placeholder="至少6位，字母数字组合"
                                show-password />
                        </el-form-item>
                        <el-form-item label="确认密码" prop="confirmPassword">
                            <el-input v-model="registerForm.confirmPassword" type="password" placeholder="再次输入密码"
                                show-password />
                        </el-form-item>
                        <el-form-item>
                            <el-button type="primary" @click="handleRegister" :loading="registerLoading"
                                style="width: 100%">
                                立即注册
                            </el-button>
                        </el-form-item>
                    </el-form>
                    <div class="terms">注册代表同意《校园圈用户协议》及隐私政策</div>
                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>

<script setup lang="ts">
/**
 * 登录/注册页面 — 对接真实后端 API
 */
import { ref, reactive } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import { register as apiRegister } from '@/services/auth'
import type { RegisterPayload } from '@/types'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref<'login' | 'register'>('login')
const loginLoading = ref(false)
const registerLoading = ref(false)

// 登录表单
const loginForm = reactive({
    student_id: '',   // 注意字段名
    password: '',
})
const loginRules: FormRules = {
    student_id: [{ required: true, message: '请输入学号/工号', trigger: 'blur' }],
    password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}
const loginFormRef = ref<FormInstance>()

// 注册表单
const registerForm = reactive<RegisterPayload & { confirmPassword: string }>({
    student_id: '',
    email: '',
    nickname: '',
    department: '',   // 后端可能忽略，但可传
    grade: '',
    password: '',
    confirmPassword: '',
})

// 校验函数保持不变 ...
const validateConfirm = (_rule: any, value: string, callback: (error?: Error) => void) => {
    if (value !== registerForm.password) callback(new Error('两次输入的密码不一致'))
    else callback()
}
const validateStudentId = (_rule: any, value: string, callback: (error?: Error) => void) => {
    if (value && !/^\d{6,12}$/.test(value)) callback(new Error('学号/工号应为6-12位数字'))
    else callback()
}
const validateEmailCampus = (_rule: any, value: string, callback: (error?: Error) => void) => {
    if (value && !/^[^\s@]+@([^\s@]+\.)?(edu\.[a-z]{2,}|edu\.cn|edu)$/i.test(value))
        callback(new Error('请填写有效的教育邮箱 (包含 .edu)'))
    else callback()
}

const registerRules: FormRules = {
    student_id: [
        { required: true, message: '学号/工号不能为空', trigger: 'blur' },
        { validator: validateStudentId, trigger: 'blur' },
    ],
    email: [
        { required: true, message: '校园邮箱不能为空', trigger: 'blur' },
        { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
        { validator: validateEmailCampus, trigger: 'blur' },
    ],
    nickname: [{ min: 1, max: 20, message: '昵称长度1-20字符', trigger: 'blur' }],
    password: [
        { required: true, message: '密码不能为空', trigger: 'blur' },
        { min: 6, message: '密码长度至少6位', trigger: 'blur' },
    ],
    confirmPassword: [
        { required: true, message: '请再次输入密码', trigger: 'blur' },
        { validator: validateConfirm, trigger: 'blur' },
    ],
}
const registerFormRef = ref<FormInstance>()

// 切换 Tab 逻辑不变
const handleTabClick = () => {
    if (activeTab.value === 'login') {
        registerFormRef.value?.resetFields()
        loginFormRef.value?.clearValidate()
    } else {
        loginFormRef.value?.resetFields()
        registerFormRef.value?.clearValidate()
    }
}

// 登录处理
const handleLogin = async () => {
    if (!loginFormRef.value) return
    await loginFormRef.value.validate(async (valid) => {
        if (valid) {
            loginLoading.value = true
            try {
                await userStore.login(loginForm.student_id, loginForm.password)
                ElMessage.success('登录成功')
                await router.push('/')
            } catch (error: any) {
                // 错误已在拦截器中提示，这里可忽略或再次提示
            } finally {
                loginLoading.value = false
            }
        }
    })
}

// 注册处理
const handleRegister = async () => {
    if (!registerFormRef.value) return
    await registerFormRef.value.validate(async (valid) => {
        if (valid) {
            registerLoading.value = true
            try {
                const { confirmPassword, ...registerData } = registerForm
                // 确保字段名与后端一致
                await apiRegister({
                    student_id: registerData.student_id,
                    email: registerData.email,
                    password: registerData.password,
                    nickname: registerData.nickname || undefined,
                    // department 和 grade 若后端暂时不支持，可忽略，但传了也没坏处
                })
                ElMessage.success('注册成功，请登录')
                activeTab.value = 'login'
                loginForm.student_id = registerForm.student_id
                registerFormRef.value?.resetFields()
            } catch (error: any) {
                // 错误已由拦截器处理
            } finally {
                registerLoading.value = false
            }
        }
    })
}

const simulateForget = () => {
    ElMessage.info('请通过校园邮箱找回密码或联系教务处')
}
</script>

<!-- 样式部分保持不变 -->

<style scoped lang="scss">
.auth-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(145deg, #f0f7ff 0%, #e9f0fa 100%);
    padding: 1.5rem;
    position: relative;
}

.auth-card {
    max-width: 520px;
    width: 100%;
    background: rgba(255, 255, 255, 0.96);
    border-radius: 2rem;
    box-shadow: 0 20px 35px -12px rgba(0, 0, 0, 0.12);
    padding: 2rem 1.8rem 2.2rem;
    transition: box-shadow 0.2s;

    &:hover {
        box-shadow: 0 28px 40px -16px rgba(0, 0, 0, 0.18);
    }
}

.brand {
    text-align: center;
    margin-bottom: 2rem;

    h1 {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        background-clip: text;
        -webkit-background-clip: text;
        color: transparent;
        margin-bottom: 0.5rem;
    }

    .sub {
        color: #5b6e8c;
        font-size: 0.9rem;
        border-top: 1px solid #e2e8f0;
        display: inline-block;
        padding-top: 0.5rem;
    }
}

:root {
    --el-color-primary: #2e5bff;
}

.el-input__wrapper {
    border-radius: 14px;
}

.el-button--primary {
    border-radius: 40px;
    font-weight: 600;
    background: linear-gradient(105deg, #2e5bff 0%, #3c6eff 100%);
    border: none;

    &:hover {
        background: linear-gradient(105deg, #1f4ce6 0%, #2e5bff 100%);
        transform: translateY(-1px);
    }
}

.extra-links {
    display: flex;
    justify-content: flex-end;
    margin-top: -0.5rem;
    margin-bottom: 1rem;

    a {
        color: #5b6e8c;
        text-decoration: none;
        font-size: 0.8rem;

        &:hover {
            color: #2e5bff;
        }
    }
}

.form-row {
    display: flex;
    gap: 1rem;

    .el-form-item {
        flex: 1;
    }
}

.demo-hint,
.terms {
    text-align: center;
    font-size: 0.75rem;
    color: #8a9bb0;
    margin-top: 0.5rem;
}

.decor-dot {
    position: fixed;
    width: 240px;
    height: 240px;
    border-radius: 50%;
    z-index: -1;

    &.dot1 {
        top: -80px;
        right: -80px;
        background: radial-gradient(circle, rgba(46, 91, 255, 0.04) 0%, transparent 70%);
    }

    &.dot2 {
        bottom: -60px;
        left: -60px;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(18, 185, 129, 0.05) 0%, transparent 70%);
    }
}

@media (max-width: 550px) {
    .auth-card {
        padding: 1.5rem;
    }

    .form-row {
        flex-direction: column;
        gap: 0;
    }
}
</style>