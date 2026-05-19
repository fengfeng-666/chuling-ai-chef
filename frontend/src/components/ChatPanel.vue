<template>
  <div class="chat-panel">
    <!-- 消息列表 -->
    <div class="chat-messages" ref="messagesRef" @scroll="handleScroll">
      <!-- 欢迎语 -->
      <div v-if="messages.length === 0 && !loading" class="welcome">
        <div class="welcome-avatar">🧑‍🍳</div>
        <h3>{{ greeting }}</h3>
        <p>告诉我你想吃什么，或者上传食材图片<br />我来帮你推荐最合适的菜品~</p>
        <div class="quick-asks">
          <button
            v-for="q in quickQuestions"
            :key="q"
            class="quick-btn"
            @click="sendText(q)"
          >{{ q }}</button>
        </div>
      </div>

      <!-- 消息气泡 -->
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        class="message-row"
        :class="msg.role"
      >
        <div v-if="msg.role === 'ai'" class="avatar">
          <span class="avatar-emoji">🧑‍🍳</span>
        </div>

        <div class="bubble-wrap">
          <!-- 图片附件 -->
          <div v-if="msg.image" class="msg-image">
            <img :src="msg.image" alt="上传的图片" />
          </div>

          <!-- 识别食材标签 -->
          <div v-if="msg.ingredients?.length" class="msg-ingredients">
            <span
              v-for="(ing, i) in msg.ingredients"
              :key="i"
              class="ing-chip"
            >{{ ing }}</span>
          </div>

          <!-- 文字内容 -->
          <div v-if="msg.content || msg._streaming" class="bubble" :class="{ 'is-streaming': msg._streaming }">
            <span v-html="renderContent(msg.content)"></span>
            <span v-if="msg._streaming" class="streaming-cursor">|</span>
          </div>

          <!-- 内嵌菜谱卡片 -->
          <div v-if="msg.recipes?.length" class="msg-recipes">
            <div
              v-for="(recipe, ri) in msg.recipes"
              :key="ri"
              class="inline-recipe"
              @click="$emit('select-recipe', recipe)"
            >
              <div class="ir-header">
                <span class="ir-name">{{ recipe.name }}</span>
                <span class="ir-badge" :class="recipe.difficulty">{{ recipe.difficulty }}</span>
              </div>
              <p class="ir-desc">{{ recipe.description }}</p>
              <div class="ir-footer">
                <span class="ir-time">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
                  </svg>
                  {{ recipe.cooking_time }}
                </span>
                <span class="ir-steps">{{ recipe.steps?.length || 0 }} 步</span>
                <span class="ir-link">查看做法 →</span>
              </div>
            </div>
          </div>

          <!-- AI 消息操作 -->
          <div v-if="msg.role === 'ai' && msg.content && !msg._streaming" class="msg-actions">
            <button class="action-btn" title="复制回复" @click="copyMessage(msg.content)">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></svg>
            </button>
            <button class="action-btn" title="重新生成" @click="emit('regenerate', idx)">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10" /><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" /></svg>
            </button>
          </div>
        </div>

        <div v-if="msg.role === 'user'" class="avatar">
          <span class="avatar-emoji">👤</span>
        </div>
      </div>

      <!-- 加载中（流式消息时不显示） -->
      <div v-if="loading && !streamingMsgExists" class="message-row ai">
        <div class="avatar">
          <span class="avatar-emoji">🧑‍🍳</span>
        </div>
        <div class="bubble-wrap">
          <div class="typing-indicator">
            <span></span><span></span><span></span>
            <span class="typing-text">{{ typingText }}</span>
          </div>
        </div>
      </div>

      <button v-if="showScrollBtn" class="scroll-bottom-btn" @click="scrollToBottom()">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>
    </div>

    <!-- 附件预览 -->
    <div v-if="attachedImage" class="attach-preview">
      <img :src="attachedImage.preview" alt="附件预览" />
      <button class="remove-attach" @click="removeAttachment">✕</button>
    </div>

    <!-- 输入区 -->
    <div class="chat-input">
      <button class="attach-btn" @click="triggerFileInput">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
        </svg>
      </button>
      <input
        ref="fileInputRef"
        type="file"
        accept="image/jpeg,image/png,image/gif,image/webp"
        hidden
        @change="handleFileAttach"
      />
      <textarea
        ref="inputRef"
        v-model="inputText"
        class="text-input"
        placeholder="输入你想吃什么，或上传食材图片..."
        rows="1"
        @keydown="handleInputKeydown"
        @input="autoResize"
      />
      <button
        v-if="streamingMsgExists"
        class="stop-btn"
        @click="emit('stop')"
        title="停止生成"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" stroke="none">
          <rect x="4" y="4" width="16" height="16" rx="2" />
        </svg>
      </button>
      <button
        v-else
        class="send-btn"
        :disabled="!inputText.trim() && !attachedImage"
        @click="sendText(inputText)"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="22" y1="2" x2="11" y2="13" />
          <polygon points="22 2 15 22 11 13 2 9 22 2" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue'
import { marked } from 'marked'

marked.setOptions({ breaks: true })

const emit = defineEmits(['select-recipe', 'send', 'stop', 'regenerate'])
const props = defineProps({
  messages: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const inputText = ref('')
const attachedImage = ref(null)
const messagesRef = ref(null)
const fileInputRef = ref(null)
const inputRef = ref(null)

const quickQuestions = [
  '推荐几道简单快手的家常菜',
  '我想吃川菜，要有肉',
  '今天想吃清淡的',
  '一个人吃饭，推荐个单人餐',
]

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了，来份夜宵吧'
  if (h < 9) return '早上好！来份元气早餐吧'
  if (h < 12) return '上午好！我是厨灵'
  if (h < 14) return '中午好！该吃午饭啦'
  if (h < 18) return '下午好！想来点下午茶吗'
  return '晚上好！今晚做什么好吃的'
})

const typingPhrases = ['正在思考…', '正在查阅菜谱…', '正在整理步骤…', '马上就好…']
const typingText = ref(typingPhrases[0])
let typingTimer = null
onMounted(() => {
  let i = 0
  typingTimer = setInterval(() => {
    i = (i + 1) % typingPhrases.length
    typingText.value = typingPhrases[i]
  }, 2000)
})
onUnmounted(() => {
  clearInterval(typingTimer)
})

function handleInputKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendText(inputText.value)
  }
}

function autoResize() {
  const el = inputRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

async function sendText(text) {
  const trimmed = text.trim()
  if (!trimmed && !attachedImage.value) return

  const imageFile = attachedImage.value?.file || null
  attachedImage.value = null
  inputText.value = ''
  emit('send', { text: trimmed || '帮我看看这些食材能做什么菜', imageFile })
  await scrollToBottom()
  // Reset textarea height
  const el = inputRef.value
  if (el) el.style.height = 'auto'
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

function handleFileAttach(e) {
  const file = e.target.files?.[0]
  if (!file) return
  const allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!allowed.includes(file.type)) return
  attachedImage.value = {
    file,
    preview: URL.createObjectURL(file),
  }
  inputRef.value?.focus()
}

function removeAttachment() {
  attachedImage.value = null
  if (fileInputRef.value) fileInputRef.value.value = ''
}

async function copyMessage(text) {
  try {
    await navigator.clipboard.writeText(text)
  } catch {
    // Fallback for older browsers
    const ta = document.createElement('textarea')
    ta.value = text
    ta.style.position = 'fixed'
    ta.style.left = '-9999px'
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
  }
}

function renderContent(text) {
  if (!text) return ''
  return marked.parse(text)
}

const streamingMsgExists = computed(() =>
  props.messages.some((m) => m.role === 'ai' && m._streaming)
)

const userScrolledUp = ref(false)
const showScrollBtn = ref(false)

function handleScroll() {
  const el = messagesRef.value
  if (!el) return
  const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 80
  if (atBottom) {
    userScrolledUp.value = false
    showScrollBtn.value = false
  } else {
    userScrolledUp.value = true
    showScrollBtn.value = true
  }
}

async function scrollToBottom() {
  await nextTick()
  const el = messagesRef.value
  if (el) {
    el.scrollTop = el.scrollHeight
    userScrolledUp.value = false
    showScrollBtn.value = false
  }
}

watch(
  () => props.messages.map((m) => (m._streaming ? m.content + '|' : m.content)).join(''),
  () => { if (!userScrolledUp.value) scrollToBottom() },
)
watch(() => props.loading, (val) => { if (val) scrollToBottom() })
</script>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 20px;
  overflow: hidden;
}

/* Messages */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
}

.scroll-bottom-btn {
  position: absolute;
  bottom: 16px;
  right: 50%;
  transform: translateX(50%);
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(30, 30, 50, 0.9);
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  backdrop-filter: blur(4px);
  animation: fadeInUp 0.2s ease;
  transition: all 0.2s;
}
.scroll-bottom-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.4);
  color: #a5b4fc;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateX(50%) translateY(8px); }
  to { opacity: 1; transform: translateX(50%) translateY(0); }
}

.welcome {
  text-align: center;
  padding: 40px 20px 20px;
}
.welcome-avatar {
  font-size: 3rem;
  margin-bottom: 12px;
}
.welcome h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 8px;
}
.welcome p {
  font-size: 0.88rem;
  color: #94a3b8;
  margin: 0 0 20px;
  line-height: 1.6;
}
.quick-asks {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}
.quick-btn {
  font-size: 0.8rem;
  font-family: inherit;
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid rgba(102, 126, 234, 0.25);
  background: rgba(102, 126, 234, 0.08);
  color: #a5b4fc;
  cursor: pointer;
  transition: all 0.2s;
}
.quick-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
  color: #c7d2fe;
}

/* Message Rows */
.message-row {
  display: flex;
  gap: 10px;
  max-width: 85%;
  animation: msgIn 0.3s ease;
}
@keyframes msgIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.message-row.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}
.message-row.ai {
  align-self: flex-start;
}

.avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
}
.avatar-emoji {
  font-size: 1.2rem;
  line-height: 1;
}

.bubble-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.bubble {
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 0.9rem;
  line-height: 1.7;
  word-break: break-word;
}
.message-row.user .bubble {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #f1f5f9;
  border-bottom-right-radius: 6px;
}
.message-row.ai .bubble {
  background: rgba(255, 255, 255, 0.06);
  color: #e2e8f0;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-bottom-left-radius: 6px;
}
.bubble :deep(strong) {
  color: #f1f5f9;
}
.bubble :deep(p) {
  margin: 0 0 0.5em;
}
.bubble :deep(p:last-child) {
  margin-bottom: 0;
}
.bubble :deep(ul), .bubble :deep(ol) {
  margin: 0.4em 0;
  padding-left: 1.4em;
}
.bubble :deep(li) {
  margin-bottom: 0.25em;
}
.bubble :deep(h1), .bubble :deep(h2), .bubble :deep(h3) {
  font-size: 1.05em;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0.8em 0 0.3em;
}
.bubble :deep(h1:first-child), .bubble :deep(h2:first-child), .bubble :deep(h3:first-child) {
  margin-top: 0;
}
.bubble :deep(code) {
  font-size: 0.85em;
  padding: 1px 5px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  font-family: 'Consolas', 'Courier New', monospace;
}
.bubble :deep(pre) {
  margin: 0.5em 0;
  padding: 10px 14px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.3);
  overflow-x: auto;
}
.bubble :deep(pre code) {
  padding: 0;
  background: none;
}
.bubble :deep(blockquote) {
  margin: 0.5em 0;
  padding: 4px 12px;
  border-left: 3px solid rgba(102, 126, 234, 0.4);
  color: #94a3b8;
}
.bubble :deep(em) {
  color: #cbd5e1;
}
.bubble :deep(hr) {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  margin: 0.8em 0;
}
.bubble :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0.5em 0;
  font-size: 0.85em;
}
.bubble :deep(th), .bubble :deep(td) {
  padding: 6px 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-align: left;
}
.bubble :deep(th) {
  background: rgba(255, 255, 255, 0.06);
  font-weight: 600;
}

/* Message actions */
.msg-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
  margin-top: 2px;
}
.message-row:hover .msg-actions {
  opacity: 1;
}
.action-btn {
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.06);
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}
.action-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #e2e8f0;
}

.streaming-cursor {
  display: inline-block;
  color: #a5b4fc;
  font-weight: 700;
  animation: blink 0.7s step-end infinite;
}
@keyframes blink {
  50% { opacity: 0; }
}

/* Image in message */
.msg-image img {
  max-width: 240px;
  max-height: 200px;
  border-radius: 12px;
  display: block;
}

/* Ingredients tags */
.msg-ingredients {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.ing-chip {
  font-size: 0.76rem;
  padding: 3px 10px;
  border-radius: 12px;
  background: rgba(52, 211, 153, 0.12);
  color: #6ee7b7;
  border: 1px solid rgba(52, 211, 153, 0.2);
}

/* Inline recipe cards */
.msg-recipes {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.inline-recipe {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  padding: 14px 16px;
  cursor: pointer;
  transition: all 0.2s;
}
.inline-recipe:hover {
  border-color: rgba(102, 126, 234, 0.35);
  background: rgba(255, 255, 255, 0.08);
  transform: translateX(3px);
}
.ir-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.ir-name {
  font-size: 0.92rem;
  font-weight: 600;
  color: #f1f5f9;
}
.ir-badge {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(102, 126, 234, 0.12);
  color: #a5b4fc;
}
.ir-badge.简单 {
  background: rgba(52, 211, 153, 0.12);
  color: #6ee7b7;
}
.ir-badge.中等 {
  background: rgba(251, 191, 36, 0.12);
  color: #fcd34d;
}
.ir-badge.困难 {
  background: rgba(248, 113, 113, 0.12);
  color: #fca5a5;
}
.ir-desc {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0 0 10px;
}
.ir-footer {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 0.78rem;
}
.ir-time {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #64748b;
}
.ir-steps {
  color: #64748b;
}
.ir-link {
  margin-left: auto;
  color: #818cf8;
  font-weight: 500;
}
.ir-link:hover {
  color: #a5b4fc;
}

/* Typing indicator */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  border-bottom-left-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.typing-indicator span:not(.typing-text) {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #94a3b8;
  animation: typing 1.4s infinite;
  flex-shrink: 0;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
.typing-indicator .typing-text {
  width: auto;
  height: auto;
  border-radius: 0;
  background: transparent;
  animation: none;
  font-size: 0.82rem;
  color: #94a3b8;
  margin-left: 8px;
}
@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

/* Attachment preview */
.attach-preview {
  position: relative;
  display: inline-block;
  align-self: flex-end;
  margin: 0 20px 4px;
}
.attach-preview img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 10px;
  border: 2px solid rgba(102, 126, 234, 0.4);
}
.remove-attach {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  border: none;
  border-radius: 50%;
  background: #ef4444;
  color: #fff;
  font-size: 0.7rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Input area */
.chat-input {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.02);
}
.attach-btn {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.06);
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.attach-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  color: #a5b4fc;
}
.text-input {
  flex: 1;
  padding: 10px 14px;
  font-size: 0.9rem;
  font-family: inherit;
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  outline: none;
  transition: border-color 0.2s;
  resize: none;
  line-height: 1.5;
  max-height: 120px;
}
.text-input::placeholder {
  color: #64748b;
}
.text-input:focus {
  border-color: rgba(102, 126, 234, 0.4);
}
.send-btn {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea, #f857a6);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.35);
}
.send-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.stop-btn {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 12px;
  background: #ef4444;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  animation: pulse-stop 1.5s ease-in-out infinite;
}
.stop-btn:hover {
  background: #dc2626;
  transform: scale(1.05);
}
@keyframes pulse-stop {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
}
</style>
