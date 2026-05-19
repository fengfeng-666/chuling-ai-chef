<template>
  <div class="wheel-overlay" @click.self="$emit('close')">
    <div class="wheel-panel">
      <button class="close-btn" @click="$emit('close')">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>

      <h2 class="wheel-title">命运大转盘</h2>
      <p class="wheel-sub">让命运决定今天吃什么！</p>

      <div class="canvas-wrap">
        <canvas ref="canvasRef" :width="canvasSize" :height="canvasSize"></canvas>
        <div class="pointer"></div>
      </div>

      <button class="btn-spin" :disabled="spinning" @click="spin">
        <template v-if="!spinning">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
          {{ result ? '再来一次' : '开始旋转' }}
        </template>
        <template v-else>
          <div class="btn-spinner"></div>
          旋转中…
        </template>
      </button>

      <div v-if="result" class="wheel-result">
        <div class="result-emoji">🎉</div>
        <p class="result-label">命运选择了</p>
        <p class="result-name">{{ result }}</p>
        <button class="btn-recipe" :disabled="loading" @click="lookUpRecipe">
          <template v-if="!loading">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            查看做法
          </template>
          <template v-else>
            <div class="btn-spinner"></div>
            AI 正在生成做法…
          </template>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'

defineProps({
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'lookup-recipe'])

const dishes = [
  '番茄炒蛋', '红烧排骨', '宫保鸡丁', '麻婆豆腐', '糖醋里脊',
  '水煮鱼', '回锅肉', '酸辣土豆丝', '鱼香肉丝', '京酱肉丝',
  '干煸豆角', '地三鲜', '可乐鸡翅', '蒜蓉西兰花', '洋葱炒肉',
  '红烧牛肉面', '蛋炒饭', '锅包肉', '辣子鸡', '葱爆羊肉',
]

const colors = [
  '#667eea', '#f857a6', '#43e97b', '#f093fb', '#4facfe',
  '#fa709a', '#30cfd0', '#a8edea', '#fccb90', '#d57eeb',
  '#f093fb', '#667eea', '#43e97b', '#4facfe', '#fa709a',
  '#f857a6', '#30cfd0', '#d57eeb', '#fccb90', '#a8edea',
]

const canvasRef = ref(null)
const canvasSize = 340
const spinning = ref(false)
const result = ref('')
let currentAngle = 0

function drawWheel() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const cx = canvasSize / 2
  const cy = canvasSize / 2
  const radius = canvasSize / 2 - 6
  const sliceAngle = (2 * Math.PI) / dishes.length

  ctx.clearRect(0, 0, canvasSize, canvasSize)

  dishes.forEach((dish, i) => {
    const startAngle = currentAngle + i * sliceAngle
    const endAngle = startAngle + sliceAngle

    // Slice
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.arc(cx, cy, radius, startAngle, endAngle)
    ctx.closePath()
    ctx.fillStyle = colors[i]
    ctx.fill()
    ctx.strokeStyle = 'rgba(255,255,255,0.15)'
    ctx.lineWidth = 2
    ctx.stroke()

    // Text
    ctx.save()
    ctx.translate(cx, cy)
    const textAngle = startAngle + sliceAngle / 2
    ctx.rotate(textAngle)
    ctx.textAlign = 'right'
    ctx.fillStyle = '#fff'
    ctx.font = 'bold 13px "Noto Sans SC", sans-serif'
    ctx.shadowColor = 'rgba(0,0,0,0.3)'
    ctx.shadowBlur = 4
    ctx.fillText(dish, radius - 16, 5)
    ctx.restore()
  })

  // Center circle
  ctx.beginPath()
  ctx.arc(cx, cy, 32, 0, 2 * Math.PI)
  ctx.fillStyle = '#1e1b4b'
  ctx.fill()
  ctx.strokeStyle = 'rgba(255,255,255,0.2)'
  ctx.lineWidth = 2
  ctx.stroke()
}

function spin() {
  if (spinning.value) return
  spinning.value = true
  result.value = ''

  const spins = 4 + Math.random() * 6 // 4-10 full rotations
  const targetAngle = currentAngle + spins * 2 * Math.PI
  const duration = 4000 + Math.random() * 2000 // 4-6 seconds

  const startAngle = currentAngle
  const startTime = performance.now()

  function animate(now) {
    const elapsed = now - startTime
    const progress = Math.min(elapsed / duration, 1)
    // Ease out cubic
    const eased = 1 - Math.pow(1 - progress, 3)
    currentAngle = startAngle + (targetAngle - startAngle) * eased
    drawWheel()

    if (progress < 1) {
      requestAnimationFrame(animate)
    } else {
      // Determine result
      const normalizedAngle = currentAngle % (2 * Math.PI)
      const sliceAngle = (2 * Math.PI) / dishes.length
      // Pointer is at top (3π/2 position since 0 is at 3 o'clock)
      const pointerAngle = (2 * Math.PI - normalizedAngle + Math.PI / 2) % (2 * Math.PI)
      const index = Math.floor(pointerAngle / sliceAngle) % dishes.length
      result.value = dishes[index]
      spinning.value = false
    }
  }

  requestAnimationFrame(animate)
}

async function lookUpRecipe() {
  if (result.value) {
    emit('lookup-recipe', result.value)
  }
}

onMounted(() => {
  nextTick(() => drawWheel())
})
</script>

<style scoped>
.wheel-overlay {
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

.wheel-panel {
  position: relative;
  background: linear-gradient(160deg, #1e1b4b 0%, #1e293b 100%);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 24px;
  padding: 36px 32px 32px;
  max-width: 440px;
  width: 100%;
  text-align: center;
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

.wheel-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 4px;
}
.wheel-sub {
  font-size: 0.88rem;
  color: #94a3b8;
  margin: 0 0 24px;
}

.canvas-wrap {
  position: relative;
  display: inline-block;
}
.pointer {
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 12px solid transparent;
  border-right: 12px solid transparent;
  border-top: 22px solid #f857a6;
  filter: drop-shadow(0 2px 6px rgba(248, 87, 166, 0.5));
  z-index: 10;
}

.btn-spin {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 24px;
  padding: 14px 40px;
  font-size: 1.05rem;
  font-family: inherit;
  font-weight: 600;
  color: #fff;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  background: linear-gradient(135deg, #667eea 0%, #f857a6 100%);
  transition: all 0.3s;
  letter-spacing: 1px;
}
.btn-spin:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
}
.btn-spin:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
.btn-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

.wheel-result {
  margin-top: 24px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  animation: popIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes popIn {
  from { opacity: 0; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}
.result-emoji {
  font-size: 2.5rem;
  margin-bottom: 4px;
}
.result-label {
  font-size: 0.82rem;
  color: #64748b;
  margin: 0 0 4px;
}
.result-name {
  font-size: 1.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea, #f857a6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 16px;
}
.btn-recipe {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 22px;
  font-size: 0.85rem;
  font-family: inherit;
  font-weight: 500;
  color: #a5b4fc;
  background: rgba(102, 126, 234, 0.12);
  border: 1px solid rgba(102, 126, 234, 0.25);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-recipe:hover {
  background: rgba(102, 126, 234, 0.22);
  color: #c7d2fe;
}
</style>
