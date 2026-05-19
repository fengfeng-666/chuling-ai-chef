import { ref } from 'vue'
import { useAuth } from './useAuth.js'

const sessions = ref([])
const activeSessionId = ref(null)
const messages = ref([])

export function useChat() {
  const { fetchWithAuth } = useAuth()

  async function loadSessions() {
    try {
      const res = await fetchWithAuth('/api/sessions')
      const data = await res.json()
      if (data.success) sessions.value = data.sessions
    } catch (e) {
      console.error('加载会话列表失败:', e)
    }
  }

  async function loadMessages(sessionId) {
    activeSessionId.value = sessionId
    try {
      const res = await fetchWithAuth(`/api/sessions/${sessionId}/messages`)
      const data = await res.json()
      if (data.success) messages.value = data.messages
    } catch (e) {
      console.error('加载消息失败:', e)
      messages.value = []
    }
  }

  async function createSession() {
    try {
      const res = await fetchWithAuth('/api/sessions', { method: 'POST' })
      const data = await res.json()
      if (data.success && data.session) {
        sessions.value.unshift(data.session)
        activeSessionId.value = data.session.id
        messages.value = []
        return data.session.id
      }
    } catch (e) {
      console.error('创建会话失败:', e)
    }
    return null
  }

  async function deleteSession(sessionId) {
    try {
      await fetchWithAuth(`/api/sessions/${sessionId}`, { method: 'DELETE' })
      sessions.value = sessions.value.filter((s) => s.id !== sessionId)
      if (activeSessionId.value === sessionId) {
        activeSessionId.value = null
        messages.value = []
      }
    } catch (e) {
      console.error('删除会话失败:', e)
    }
  }

  async function sendChatMessage(text, imageFile) {
    const formData = new FormData()
    formData.append('message', text || '')
    if (imageFile) formData.append('file', imageFile)
    if (activeSessionId.value) formData.append('session_id', String(activeSessionId.value))

    const res = await fetchWithAuth('/api/chat', { method: 'POST', body: formData })
    const data = await res.json()

    if (!res.ok) throw new Error(data.detail || '请求失败')

    // 如果后端创建了新会话，更新 session_id
    if (data.session_id && !activeSessionId.value) {
      await loadSessions()
      activeSessionId.value = data.session_id
    }

    // 如果 AI 回复导致标题变化，刷新会话列表
    if (data.session_id) {
      await loadSessions()
    }

    return data
  }

  return {
    sessions,
    activeSessionId,
    messages,
    loadSessions,
    loadMessages,
    createSession,
    deleteSession,
    sendChatMessage,
  }
}
