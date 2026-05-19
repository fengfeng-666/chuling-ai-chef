<template>
  <div class="quiz-overlay" @click.self="$emit('close')">
    <div class="quiz-panel">
      <button class="close-btn" @click="$emit('close')">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>

      <!-- 答题中 -->
      <template v-if="!submitted">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPct + '%' }"></div>
        </div>
        <p class="step-counter">第 {{ currentStep + 1 }} / {{ questions.length }} 题</p>

        <div class="question-card" :key="currentStep">
          <div class="q-icon">{{ questions[currentStep].icon }}</div>
          <h3 class="q-title">{{ questions[currentStep].question }}</h3>
          <div class="q-options">
            <button
              v-for="(opt, oi) in questions[currentStep].options"
              :key="oi"
              class="q-option"
              :class="{ selected: answers[questions[currentStep].key] === opt }"
              @click="selectAnswer(questions[currentStep].key, opt)"
            >
              {{ opt }}
            </button>
          </div>
        </div>

        <div class="quiz-actions">
          <button v-if="currentStep > 0" class="btn-back" @click="currentStep--">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="15 18 9 12 15 6" />
            </svg>
            上一题
          </button>
          <div v-else></div>
          <button
            v-if="currentStep < questions.length - 1"
            class="btn-next"
            :disabled="!answers[questions[currentStep].key]"
            @click="currentStep++"
          >
            下一题
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </button>
          <button
            v-else
            class="btn-submit"
            :disabled="!allAnswered"
            @click="submitQuiz"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
            查看推荐
          </button>
        </div>
      </template>

      <!-- 加载中 -->
      <div v-else-if="loading" class="quiz-loading">
        <div class="spinner"></div>
        <p class="loading-text">AI 正在分析你的口味偏好…</p>
        <div class="answer-summary">
          <span v-for="(v, k) in answers" :key="k" class="summary-tag">{{ v }}</span>
        </div>
      </div>

      <!-- 结果 -->
      <template v-else-if="result">
        <h2 class="result-title">你的专属推荐</h2>
        <p class="result-reason">{{ result.recommend_reason }}</p>

        <div class="result-recipes">
          <div
            v-for="(recipe, idx) in result.recipes"
            :key="idx"
            class="result-card"
            @click="$emit('select-recipe', recipe)"
          >
            <div class="rc-header">
              <h4>{{ recipe.name }}</h4>
              <span class="rc-badge">{{ recipe.difficulty }}</span>
            </div>
            <p class="rc-desc">{{ recipe.description }}</p>
            <div class="rc-meta">
              <span>{{ recipe.cooking_time }}</span>
              <span>{{ recipe.steps?.length || 0 }} 步</span>
            </div>
          </div>
        </div>

        <button class="btn-retry" @click="resetQuiz">重新测试</button>
      </template>

      <p v-if="error" class="error-msg">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { quizRecommend } from '../api/index.js'

const emit = defineEmits(['close', 'select-recipe'])

const questions = [
  {
    key: '口味偏好',
    question: '你喜欢什么口味？',
    icon: '👅',
    options: ['香辣过瘾', '酸甜可口', '咸鲜浓郁', '清淡鲜美', '麻香四溢', '不挑口味'],
  },
  {
    key: '菜系偏好',
    question: '想吃什么菜系？',
    icon: '🍳',
    options: ['川菜', '粤菜', '湘菜', '东北菜', '日韩料理', '西餐', '东南亚风味', '随便都行'],
  },
  {
    key: '荤素偏好',
    question: '今天想怎么搭配荤素？',
    icon: '🥩',
    options: ['纯肉食主义', '荤素搭配', '今天吃素', '海鲜为主', '无偏好'],
  },
  {
    key: '烹饪方式',
    question: '偏好哪种烹饪方式？',
    icon: '🔥',
    options: ['爆炒', '清蒸', '慢炖', '烤制', '凉拌', '煎炸', '水煮', '无所谓'],
  },
  {
    key: '时间预算',
    question: '你愿意花多长时间做饭？',
    icon: '⏱️',
    options: ['15 分钟快手', '30 分钟左右', '1 小时内', '不赶时间慢慢来'],
  },
  {
    key: '难度期望',
    question: '你对自己的厨艺评价？',
    icon: '👨‍🍳',
    options: ['新手入门', '有点基础', '厨房老手', '挑战硬菜'],
  },
  {
    key: '用餐场景',
    question: '今天是什么用餐场景？',
    icon: '🍽️',
    options: ['一人独享', '二人世界', '家庭聚餐', '朋友聚会', '减脂健康餐'],
  },
  {
    key: '主食偏好',
    question: '想配什么主食？',
    icon: '🍚',
    options: ['米饭', '面食', '馒头大饼', '不需要主食', '看菜决定'],
  },
]

const currentStep = ref(0)
const answers = ref({})
const submitted = ref(false)
const loading = ref(false)
const result = ref(null)
const error = ref('')

const progressPct = computed(() => {
  const answered = Object.keys(answers.value).length
  return Math.round((answered / questions.length) * 100)
})

const allAnswered = computed(() => {
  return questions.every((q) => answers.value[q.key])
})

function selectAnswer(key, value) {
  answers.value = { ...answers.value, [key]: value }
}

async function submitQuiz() {
  loading.value = true
  error.value = ''
  submitted.value = true
  try {
    const data = await quizRecommend(answers.value)
    result.value = data
  } catch (e) {
    error.value = e.message || '推荐失败，请重试'
    submitted.value = false
  } finally {
    loading.value = false
  }
}

function resetQuiz() {
  submitted.value = false
  result.value = null
  answers.value = {}
  currentStep.value = 0
}
</script>

<style scoped>
.quiz-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: fadeIn 0.25s ease;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.quiz-panel {
  position: relative;
  background: linear-gradient(160deg, #1e1b4b 0%, #1e293b 100%);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 24px;
  padding: 36px 32px 32px;
  max-width: 540px;
  width: 100%;
  max-height: 85vh;
  overflow-y: auto;
  animation: slideUp 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(40px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.close-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.progress-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
  margin-bottom: 12px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #f857a6);
  border-radius: 2px;
  transition: width 0.4s ease;
}

.step-counter {
  text-align: center;
  font-size: 0.8rem;
  color: #64748b;
  margin: 0 0 24px;
}

.question-card {
  text-align: center;
  margin-bottom: 28px;
  animation: fadeSlideIn 0.35s ease;
}
@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.q-icon {
  font-size: 3rem;
  margin-bottom: 12px;
}
.q-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0 0 20px;
}

.q-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}
.q-option {
  padding: 10px 20px;
  font-size: 0.9rem;
  font-family: inherit;
  font-weight: 500;
  color: #cbd5e1;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.q-option:hover {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
}
.q-option.selected {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(248, 87, 166, 0.2));
  border-color: #667eea;
  color: #e2e8f0;
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
}

.quiz-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.btn-back, .btn-next, .btn-submit {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 24px;
  font-size: 0.9rem;
  font-family: inherit;
  font-weight: 500;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-back {
  background: rgba(255, 255, 255, 0.06);
  color: #94a3b8;
}
.btn-back:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #e2e8f0;
}
.btn-next, .btn-submit {
  background: linear-gradient(135deg, #667eea, #f857a6);
  color: #fff;
}
.btn-next:disabled, .btn-submit:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none !important;
}
.btn-next:hover:not(:disabled), .btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(102, 126, 234, 0.35);
}

/* Loading */
.quiz-loading {
  text-align: center;
  padding: 40px 0;
}
.spinner {
  width: 44px;
  height: 44px;
  margin: 0 auto 16px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.loading-text {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.92rem;
  margin-bottom: 20px;
}
.answer-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}
.summary-tag {
  font-size: 0.78rem;
  padding: 4px 12px;
  border-radius: 20px;
  background: rgba(102, 126, 234, 0.15);
  color: #a5b4fc;
}

/* Results */
.result-title {
  text-align: center;
  font-size: 1.5rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 8px;
}
.result-reason {
  text-align: center;
  font-size: 0.88rem;
  color: #94a3b8;
  margin: 0 0 24px;
  line-height: 1.6;
}

.result-recipes {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}
.result-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 18px;
  cursor: pointer;
  transition: all 0.2s;
}
.result-card:hover {
  border-color: rgba(102, 126, 234, 0.3);
  background: rgba(255, 255, 255, 0.07);
  transform: translateX(4px);
}
.rc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.rc-header h4 {
  font-size: 1.05rem;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0;
}
.rc-badge {
  font-size: 0.72rem;
  padding: 3px 10px;
  border-radius: 12px;
  background: rgba(102, 126, 234, 0.15);
  color: #a5b4fc;
}
.rc-desc {
  font-size: 0.82rem;
  color: #94a3b8;
  margin: 0 0 10px;
}
.rc-meta {
  display: flex;
  gap: 16px;
  font-size: 0.78rem;
  color: #64748b;
}

.btn-retry {
  display: block;
  margin: 0 auto;
  padding: 12px 32px;
  font-size: 0.88rem;
  font-family: inherit;
  font-weight: 500;
  color: #94a3b8;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-retry:hover {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.1);
}

.error-msg {
  text-align: center;
  color: #f87171;
  font-size: 0.85rem;
  padding: 10px 16px;
  background: rgba(248, 113, 113, 0.1);
  border-radius: 10px;
  margin-top: 16px;
}
</style>
