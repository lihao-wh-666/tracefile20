<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <el-icon size="48" class="login-icon"><Document /></el-icon>
        <h1 class="login-title">{{ t('login.title') }}</h1>
        <p class="login-subtitle">{{ t('login.subtitle') }}</p>
      </div>
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            :placeholder="t('login.username')"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            :placeholder="t('login.password')"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            {{ t('login.login') }}
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-footer">
        <p>默认账号：admin / admin123</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Document } from '@element-plus/icons-vue'
import { authApi } from '@/api'
import { useTheme } from '@/composables/useTheme'
import { useLocale } from '@/composables/useLocale'

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)

const { t } = useLocale()

onMounted(async () => {
  try {
    await authApi.getCsrfToken()
  } catch (e) {
    console.warn('获取 CSRF token 失败', e)
  }
})

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: t('login.usernameRequired'), trigger: 'blur' }
  ],
  password: [
    { required: true, message: t('login.passwordRequired'), trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await authApi.login({
        username: loginForm.username,
        password: loginForm.password
      })
      const userInfoRes = await authApi.getUserInfo()
      localStorage.setItem('user', JSON.stringify(userInfoRes.data))
      ElMessage.success(t('login.loginSuccess'))
      router.push('/dashboard')
    } catch (error) {
      const detail = error.response?.data?.detail || t('login.loginFailed')
      ElMessage.error(detail)
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-primary);
  transition: background 0.3s ease;
}

.login-box {
  width: 400px;
  padding: 40px;
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-icon {
  color: var(--primary-color);
  margin-bottom: 10px;
  transition: color 0.3s ease;
}

.login-title {
  font-size: 24px;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  font-weight: 600;
  transition: color 0.3s ease;
}

.login-subtitle {
  font-size: 14px;
  color: var(--text-tertiary);
  margin: 0;
  transition: color 0.3s ease;
}

.login-form {
  margin-top: 20px;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  background: var(--gradient-primary);
  border: none;
  transition: opacity 0.3s ease;
}

.login-btn:hover {
  opacity: 0.9;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-tertiary);
  transition: border-color 0.3s ease;
}

.login-footer p {
  font-size: 13px;
  color: var(--text-tertiary);
  margin: 0;
  transition: color 0.3s ease;
}

@media (max-width: 480px) {
  .login-box {
    width: 90%;
    padding: 30px 20px;
  }

  .login-title {
    font-size: 20px;
  }
}
</style>
