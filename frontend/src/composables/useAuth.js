import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const token = ref(localStorage.getItem('chuling_token') || '')
const user = ref(JSON.parse(localStorage.getItem('chuling_user') || 'null'))

export function useAuth() {
  const router = useRouter()
  const isLoggedIn = computed(() => !!token.value)

  function setAuth(t, u) {
    token.value = t
    user.value = u
    localStorage.setItem('chuling_token', t)
    localStorage.setItem('chuling_user', JSON.stringify(u))
  }

  function clearAuth() {
    token.value = ''
    user.value = null
    localStorage.removeItem('chuling_token')
    localStorage.removeItem('chuling_user')
  }

  async function fetchWithAuth(url, options = {}) {
    const headers = {
      ...options.headers,
      Authorization: `Bearer ${token.value}`,
    }
    // Don't set Content-Type for FormData — browser sets it with boundary
    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json'
    }

    const response = await fetch(url, { ...options, headers })

    if (response.status === 401) {
      clearAuth()
      router.push('/login')
      throw new Error('登录已过期，请重新登录')
    }

    return response
  }

  return { token, user, isLoggedIn, setAuth, clearAuth, fetchWithAuth }
}
