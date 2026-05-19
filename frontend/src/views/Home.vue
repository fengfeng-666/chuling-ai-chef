<template>
  <div class="home-layout">
    <!-- 侧边栏 -->
    <ChatSidebar
      :sessions="chat.sessions.value"
      :active-id="chat.activeSessionId.value"
      @new-session="handleNewSession"
      @select-session="handleSelectSession"
      @delete-session="handleDeleteSession"
      @select-recipe="openSteps"
    />

    <!-- 主内容区 -->
    <div class="main-area">
      <header class="home-header">
        <div class="user-bar">
          <span class="user-greeting">
            {{ isLoggedIn ? `${greetingText}，${user?.username}` : '你的对话不会被保存，' }}<router-link v-if="!isLoggedIn" to="/login" class="guest-login-link">登录后可永久保存</router-link>
          </span>
        </div>
        <h1 class="logo">厨 灵</h1>
        <p class="subtitle">拍一拍食材，秒变大厨</p>
      </header>

      <!-- 模式切换 -->
      <div class="mode-tabs">
        <button class="mode-tab" :class="{ active: activeMode === 'chat' }" @click="activeMode = 'chat'">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg>
          智能对话
        </button>
        <button class="mode-tab" :class="{ active: activeMode === 'decide' }" @click="activeMode = 'decide'">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" /><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" /><line x1="12" y1="17" x2="12.01" y2="17" /></svg>
          不知道吃什么
        </button>
      </div>

      <!-- 模式一：智能对话 -->
      <ChatPanel
        v-if="activeMode === 'chat'"
        :messages="displayMessages"
        :loading="chatLoading"
        @send="handleChatSend"
        @stop="handleStopStream"
        @regenerate="handleRegenerate"
        @select-recipe="openSteps"
      />

      <!-- 模式二：不知道吃什么 -->
      <template v-if="activeMode === 'decide'">
        <div class="decide-intro"><p>不用纠结，两种方式帮你决定今天吃什么</p></div>
        <div class="decide-cards">
          <div class="decide-card" @click="showQuiz = true">
            <div class="dc-icon-wrap quiz-icon">
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /></svg>
            </div>
            <h3 class="dc-title">口味测试</h3>
            <p class="dc-desc">回答 8 道选择题<br />AI 为你量身推荐</p>
          </div>
          <div class="decide-card" @click="showWheel = true">
            <div class="dc-icon-wrap wheel-icon">
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10" /><line x1="12" y1="2" x2="12" y2="12" /><line x1="12" y1="12" x2="16" y2="8" /><circle cx="12" cy="12" r="1" /></svg>
            </div>
            <h3 class="dc-title">命运大转盘</h3>
            <p class="dc-desc">旋转转盘随机决定<br />20 道经典家常菜</p>
          </div>
        </div>

        <div v-if="decideRecipes.length" class="recipes-section">
          <h2 class="section-title">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8h1a4 4 0 0 1 0 8h-1" /><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z" /><line x1="6" y1="1" x2="6" y2="4" /><line x1="10" y1="1" x2="10" y2="4" /><line x1="14" y1="1" x2="14" y2="4" /></svg>
            推荐菜谱
          </h2>
          <div class="recipes-grid">
            <RecipeCard v-for="(r, i) in decideRecipes" :key="i" :recipe="r" @select="openSteps" />
          </div>
        </div>
        <p v-if="decideError" class="global-error">{{ decideError }}</p>
      </template>
    </div>

    <!-- 弹窗 -->
    <CookingSteps v-if="selectedRecipe" :recipe="selectedRecipe" @close="selectedRecipe = null" />
    <FoodQuiz v-if="showQuiz" @close="showQuiz = false" @select-recipe="onQuizSelectRecipe" />
    <SpinningWheel v-if="showWheel" :loading="wheelLoading" @close="showWheel = false; wheelLoading = false" @lookup-recipe="onWheelLookup" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import RecipeCard from '../components/RecipeCard.vue'
import CookingSteps from '../components/CookingSteps.vue'
import FoodQuiz from '../components/FoodQuiz.vue'
import SpinningWheel from '../components/SpinningWheel.vue'
import ChatPanel from '../components/ChatPanel.vue'
import ChatSidebar from '../components/ChatSidebar.vue'
import { useChat } from '../composables/useChat.js'
import { useAuth } from '../composables/useAuth.js'
import { lookupDishRecipe, sendMessageStream } from '../api/index.js'

const { user, token, isLoggedIn } = useAuth()

const greetingText = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 9) return '早上好'
  if (h < 12) return '上午好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})
const chat = useChat()
const activeMode = ref('chat')
const chatLoading = ref(false)
const selectedRecipe = ref(null)
const showQuiz = ref(false)
const showWheel = ref(false)
const wheelLoading = ref(false)
const decideRecipes = ref([])
const decideError = ref('')
const guestMessages = ref([])
const streamAbortController = ref(null)

const displayMessages = computed(() =>
  isLoggedIn.value ? chat.messages.value : guestMessages.value
)

onMounted(async () => {
  if (isLoggedIn.value) {
    await chat.loadSessions()
    if (chat.sessions.value.length > 0) {
      await chat.loadMessages(chat.sessions.value[0].id)
    }
  }
})

watch(isLoggedIn, async (val) => {
  if (val) {
    await chat.loadSessions()
    if (chat.sessions.value.length > 0) {
      await chat.loadMessages(chat.sessions.value[0].id)
    }
  } else {
    chat.sessions.value = []
    chat.activeSessionId.value = null
    chat.messages.value = []
    guestMessages.value = []
  }
})

async function handleNewSession() {
  if (!isLoggedIn.value) return
  await chat.createSession()
}

async function handleSelectSession(id) {
  if (!isLoggedIn.value) return
  await chat.loadMessages(id)
}

async function handleDeleteSession(id) {
  if (!isLoggedIn.value) return
  await chat.deleteSession(id)
}

function handleChatSend({ text, imageFile }) {
  chatLoading.value = true
  const previewUrl = imageFile ? URL.createObjectURL(imageFile) : null

  // 用户消息 + AI 占位消息
  const userMsg = { role: 'user', content: text, image: previewUrl, ingredients: null, recipes: null }
  const aiMsg = { role: 'ai', content: '', ingredients: [], recipes: [], _streaming: true }

  const messages = isLoggedIn.value ? chat.messages.value : guestMessages.value
  messages.push(userMsg)
  messages.push(aiMsg)

  // 游客：构建对话历史
  let history = null
  if (!isLoggedIn.value) {
    const prev = messages.filter((m) => m !== userMsg && m !== aiMsg)
    history = prev.map((m) => ({ role: m.role, content: m.content }))
  }

  const controller = new AbortController()
  streamAbortController.value = controller

  sendMessageStream({
    message: text || '',
    imageFile: imageFile || null,
    history,
    token: isLoggedIn.value ? token.value : null,
    sessionId: isLoggedIn.value ? chat.activeSessionId.value : null,
    signal: controller.signal,
    onText: (chunk) => { aiMsg.content += chunk },
    onRecipes: (data) => {
      aiMsg.ingredients = data.ingredients || []
      aiMsg.recipes = data.recipes || []
    },
    onDone: (sessionId) => {
      aiMsg._streaming = false
      chatLoading.value = false
      streamAbortController.value = null
      if (isLoggedIn.value && sessionId) {
        if (!chat.activeSessionId.value) chat.activeSessionId.value = sessionId
        chat.loadSessions()
      }
    },
    onError: (errMsg) => {
      aiMsg.content = (aiMsg.content || '') + `\n\n[${errMsg}]`
      aiMsg._streaming = false
      chatLoading.value = false
      streamAbortController.value = null
    },
  })
}

function handleRegenerate(idx) {
  const messages = isLoggedIn.value ? chat.messages.value : guestMessages.value
  const aiMsg = messages[idx]
  const userMsg = messages[idx - 1]
  if (!aiMsg || aiMsg.role !== 'ai' || !userMsg || userMsg.role !== 'user') return
  const userText = userMsg.content
  messages.splice(idx - 1, 2)
  handleChatSend({ text: userText, imageFile: null })
}

function handleStopStream() {
  if (streamAbortController.value) {
    streamAbortController.value.abort()
    streamAbortController.value = null
  }
  const messages = isLoggedIn.value ? chat.messages.value : guestMessages.value
  const aiMsg = messages.findLast((m) => m.role === 'ai')
  if (aiMsg) {
    aiMsg._streaming = false
    if (!aiMsg.content) aiMsg.content = '[已停止生成]'
  }
  chatLoading.value = false
}

onUnmounted(() => {
  if (streamAbortController.value) {
    streamAbortController.value.abort()
  }
})

function openSteps(recipe) { selectedRecipe.value = recipe }
function onQuizSelectRecipe(recipe) { showQuiz.value = false; selectedRecipe.value = recipe }

async function onWheelLookup(dishName) {
  wheelLoading.value = true; decideError.value = ''; decideRecipes.value = []
  try {
    const data = await lookupDishRecipe(dishName)
    if (data.success && data.recipes?.length) { decideRecipes.value = data.recipes; showWheel.value = false }
    else { decideError.value = '未获取到菜谱，请重试' }
  } catch (e) {
    decideError.value = '获取菜谱失败，请重试'; showWheel.value = false
  } finally {
    wheelLoading.value = false
  }
}
</script>

<style scoped>
.home-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding: 24px 28px 40px;
  min-height: 0;
}
.home-header {
  text-align: center;
  margin-bottom: 20px;
}
.user-bar {
  text-align: right;
  margin-bottom: 4px;
}
.user-greeting {
  font-size: 0.78rem;
  color: #64748b;
}
.guest-login-link {
  color: #818cf8;
  text-decoration: none;
  font-weight: 500;
}
.guest-login-link:hover {
  color: #a5b4fc;
  text-decoration: underline;
}
.logo {
  font-size: 2rem;
  font-weight: 900;
  background: linear-gradient(135deg, #667eea, #f857a6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 4px;
  letter-spacing: 3px;
}
.subtitle {
  color: #94a3b8;
  font-size: 0.9rem;
  margin: 0;
  font-weight: 300;
  letter-spacing: 2px;
}

.mode-tabs {
  display: flex;
  gap: 2px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  padding: 4px;
  margin: 0 auto 24px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  max-width: 360px;
}
.mode-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  font-size: 0.85rem;
  font-family: inherit;
  font-weight: 500;
  color: #94a3b8;
  background: transparent;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
}
.mode-tab:hover { color: #cbd5e1; }
.mode-tab.active { background: rgba(102, 126, 234, 0.2); color: #e2e8f0; }

.decide-intro { text-align: center; margin-bottom: 20px; }
.decide-intro p { font-size: 0.88rem; color: #94a3b8; }
.decide-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 28px; max-width: 500px; margin-left: auto; margin-right: auto; }
.decide-card {
  background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 24px 18px 20px; cursor: pointer; transition: all 0.3s;
}
.decide-card:hover { transform: translateY(-3px); border-color: rgba(102, 126, 234, 0.3); background: rgba(255, 255, 255, 0.06); }
.dc-icon-wrap { width: 52px; height: 52px; border-radius: 14px; display: flex; align-items: center; justify-content: center; margin-bottom: 14px; }
.quiz-icon { background: linear-gradient(135deg, rgba(102, 126, 234, 0.25), rgba(102, 126, 234, 0.1)); color: #a5b4fc; }
.wheel-icon { background: linear-gradient(135deg, rgba(248, 87, 166, 0.25), rgba(248, 87, 166, 0.1)); color: #f9a8d4; }
.dc-title { font-size: 1.05rem; font-weight: 600; color: #f1f5f9; margin: 0 0 6px; }
.dc-desc { font-size: 0.8rem; color: #94a3b8; margin: 0; line-height: 1.5; }

.recipes-section { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.section-title { display: flex; align-items: center; gap: 8px; font-size: 1.05rem; font-weight: 600; color: rgba(255, 255, 255, 0.85); margin: 0 0 16px; }
.section-title svg { color: #f857a6; }
.recipes-grid { display: flex; flex-direction: column; gap: 12px; max-width: 500px; margin: 0 auto; }
.global-error { text-align: center; color: #f87171; font-size: 0.85rem; padding: 12px 16px; background: rgba(248, 113, 113, 0.1); border-radius: 10px; margin-top: 16px; }

@media (max-width: 640px) {
  .decide-cards { grid-template-columns: 1fr; }
}
</style>
