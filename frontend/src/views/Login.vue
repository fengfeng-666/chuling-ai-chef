<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-logo">厨 灵</h1>
      <p class="auth-sub">AI 智能菜谱，拍一拍秒变大厨</p>

      <form class="auth-form" @submit.prevent="handleLogin">
        <div class="input-group">
          <label>用户名</label>
          <input v-model="username" type="text" placeholder="请输入用户名" required />
        </div>
        <div class="input-group">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="请输入密码" required />
        </div>

        <p v-if="error" class="auth-error">{{ error }}</p>

        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? '登录中…' : '登 录' }}
        </button>
      </form>

      <p class="auth-switch">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'

const router = useRouter()
const { setAuth } = useAuth()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  if (!username.value.trim() || !password.value) {
    error.value = '请填写用户名和密码'
    return
  }
  loading.value = true
  try {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value.trim(), password: password.value }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || '登录失败')
    setAuth(data.token, data.user)
    router.push('/')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.auth-card {
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 40px 32px;
  backdrop-filter: blur(12px);
}
.auth-logo {
  text-align: center;
  font-size: 2.2rem;
  font-weight: 900;
  background: linear-gradient(135deg, #667eea, #f857a6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px;
  letter-spacing: 4px;
}
.auth-sub {
  text-align: center;
  color: #64748b;
  font-size: 0.85rem;
  margin: 0 0 32px;
}
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.input-group label {
  display: block;
  font-size: 0.82rem;
  color: #94a3b8;
  margin-bottom: 6px;
}
.input-group input {
  width: 100%;
  padding: 12px 16px;
  font-size: 0.9rem;
  font-family: inherit;
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  outline: none;
  transition: border-color 0.2s;
}
.input-group input:focus {
  border-color: rgba(102, 126, 234, 0.4);
}
.auth-error {
  color: #f87171;
  font-size: 0.82rem;
  text-align: center;
  margin: 0;
}
.btn-submit {
  padding: 14px;
  font-size: 1rem;
  font-family: inherit;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #667eea, #f857a6);
  border: none;
  border-radius: 14px;
  cursor: pointer;
  letter-spacing: 2px;
  transition: all 0.2s;
}
.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(102, 126, 234, 0.35);
}
.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.auth-switch {
  text-align: center;
  margin-top: 20px;
  font-size: 0.82rem;
  color: #64748b;
}
.auth-switch a {
  color: #818cf8;
  text-decoration: none;
  font-weight: 500;
}
.auth-switch a:hover {
  color: #a5b4fc;
}
</style>
