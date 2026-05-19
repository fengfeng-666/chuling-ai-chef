<template>
  <div class="sidebar" :class="{ collapsed }">
    <div class="sidebar-header">
      <button v-if="!collapsed" class="btn-new" @click="$emit('new-session')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        <span>新对话</span>
      </button>
      <button class="btn-toggle" @click="collapsed = !collapsed">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline v-if="collapsed" points="9 18 15 12 9 6" />
          <polyline v-else points="15 18 9 12 15 6" />
        </svg>
      </button>
    </div>

    <div v-if="!collapsed" class="sidebar-list">
      <div
        v-for="s in sessions"
        :key="s.id"
        class="session-item"
        :class="{ active: s.id === activeId }"
        @click="$emit('select-session', s.id)"
      >
        <div class="session-info">
          <span class="session-title">{{ s.title }}</span>
          <span class="session-meta">{{ s.message_count }} 条消息</span>
        </div>
        <button v-if="confirmDeleteId !== s.id" class="btn-delete" @click.stop="confirmDeleteId = s.id" title="删除">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
        <div v-else class="confirm-delete">
          <span class="confirm-text">删除?</span>
          <button class="confirm-yes" @click.stop="handleDelete(s.id)">是</button>
          <button class="confirm-no" @click.stop="confirmDeleteId = null">否</button>
        </div>
      </div>

      <div v-if="sessions.length === 0" class="empty-hint">暂无对话记录</div>

      <div v-if="favorites.length > 0" class="fav-section">
        <div class="fav-section-title">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" /></svg>
          我的收藏
        </div>
        <div
          v-for="f in favorites"
          :key="f.name"
          class="fav-item"
          @click="$emit('select-recipe', f)"
        >
          <span class="fav-name">{{ f.name }}</span>
          <span class="fav-diff" :class="f.difficulty">{{ f.difficulty }}</span>
        </div>
      </div>
    </div>

    <div v-if="!collapsed" class="sidebar-footer">
      <template v-if="isLoggedIn">
        <span class="footer-user">{{ user?.username }}</span>
        <button class="btn-logout" @click="handleLogout">退出登录</button>
      </template>
      <template v-else>
        <button class="btn-login" @click="router.push('/login')">登录</button>
        <button class="btn-register" @click="router.push('/register')">注册</button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'
import { useFavorites } from '../composables/useFavorites.js'

defineProps({
  sessions: { type: Array, default: () => [] },
  activeId: { type: Number, default: null },
})

const emit = defineEmits(['new-session', 'select-session', 'delete-session', 'select-recipe'])
const { favorites } = useFavorites()

const router = useRouter()
const { user, isLoggedIn, clearAuth } = useAuth()
const collapsed = ref(false)
const confirmDeleteId = ref(null)

function handleDelete(id) {
  confirmDeleteId.value = null
  emit('delete-session', id)
}

function handleLogout() {
  clearAuth()
}
</script>

<style scoped>
.sidebar {
  width: 240px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.015);
  transition: width 0.25s ease;
  overflow: hidden;
}
.sidebar.collapsed {
  width: 52px;
}
.sidebar.collapsed .sidebar-header {
  justify-content: center;
}

.sidebar-header {
  display: flex;
  gap: 6px;
  padding: 14px 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}
.btn-new {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 12px;
  font-size: 0.82rem;
  font-family: inherit;
  font-weight: 500;
  color: #e2e8f0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.btn-new:hover { opacity: 0.9; }
.btn-toggle {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.04);
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.btn-toggle:hover { background: rgba(255, 255, 255, 0.08); color: #e2e8f0; }

.sidebar-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.session-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
  margin-bottom: 2px;
}
.session-item:hover { background: rgba(255, 255, 255, 0.04); }
.session-item.active { background: rgba(102, 126, 234, 0.12); }
.session-info {
  flex: 1;
  min-width: 0;
}
.session-title {
  display: block;
  font-size: 0.82rem;
  color: #cbd5e1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.session-item.active .session-title { color: #e2e8f0; font-weight: 500; }
.session-meta {
  font-size: 0.7rem;
  color: #64748b;
}
.btn-delete {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.15s;
}
.session-item:hover .btn-delete { opacity: 1; }
.btn-delete:hover { background: rgba(239, 68, 68, 0.15); color: #f87171; }
.confirm-delete {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}
.confirm-text {
  font-size: 0.7rem;
  color: #f87171;
}
.confirm-yes, .confirm-no {
  font-size: 0.68rem;
  font-family: inherit;
  padding: 2px 8px;
  border-radius: 5px;
  border: none;
  cursor: pointer;
}
.confirm-yes {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
}
.confirm-no {
  background: rgba(255, 255, 255, 0.08);
  color: #94a3b8;
}

.empty-hint {
  text-align: center;
  padding: 24px 12px;
  font-size: 0.78rem;
  color: #475569;
}

.fav-section {
  margin: 4px 8px;
  padding: 8px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}
.fav-section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.72rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 6px 4px;
  margin-bottom: 4px;
}
.fav-section-title svg {
  color: #fbbf24;
}
.fav-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}
.fav-item:hover {
  background: rgba(251, 191, 36, 0.08);
}
.fav-name {
  font-size: 0.8rem;
  color: #cbd5e1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.fav-diff {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.06);
  color: #64748b;
  flex-shrink: 0;
}
.fav-diff.简单 { color: #6ee7b7; }
.fav-diff.中等 { color: #fcd34d; }
.fav-diff.困难 { color: #fca5a5; }

.sidebar-footer {
  padding: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.footer-user {
  font-size: 0.78rem;
  color: #94a3b8;
  text-align: center;
  padding: 4px 0;
}
.btn-logout {
  width: 100%;
  padding: 8px;
  font-size: 0.78rem;
  font-family: inherit;
  color: #64748b;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-logout:hover { color: #f87171; border-color: rgba(239, 68, 68, 0.2); }
.btn-login {
  width: 100%;
  padding: 8px;
  font-size: 0.82rem;
  font-family: inherit;
  font-weight: 500;
  color: #e2e8f0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-login:hover { opacity: 0.9; }
.btn-register {
  width: 100%;
  padding: 8px;
  font-size: 0.78rem;
  font-family: inherit;
  color: #94a3b8;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-register:hover { color: #e2e8f0; border-color: rgba(255, 255, 255, 0.2); }
</style>
