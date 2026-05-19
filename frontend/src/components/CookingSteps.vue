<template>
  <div v-if="recipe" class="cooking-steps-overlay" @click.self="$emit('close')">
    <div class="cooking-steps-panel">
      <button class="close-btn" @click="$emit('close')">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>

      <button class="fav-btn-panel" :class="{ active: isFav }" @click="toggleFavorite(recipe)" :title="isFav ? '取消收藏' : '收藏'">
        <svg width="18" height="18" viewBox="0 0 24 24" :fill="isFav ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
        </svg>
      </button>

      <div class="panel-header">
        <span class="panel-badge">{{ recipe.difficulty }}</span>
        <h2 class="panel-title">{{ recipe.name }}</h2>
        <p class="panel-desc">{{ recipe.description }}</p>
        <div class="panel-meta">
          <span class="meta-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
            {{ recipe.cooking_time }}
          </span>
          <span class="meta-item">{{ recipe.steps?.length || 0 }} 步完成</span>
        </div>
      </div>

      <div class="ingredients-bar">
        <span
          v-for="(ing, idx) in recipe.ingredients_needed"
          :key="idx"
          class="ing-chip"
          :class="{ 'is-main': isRecognized(ing), checked: checkedIngredients.has(ing) }"
          @click="toggleIngredient(ing)"
        >
          <span class="check-box">{{ checkedIngredients.has(ing) ? '✓' : '' }}</span>
          {{ ing }}
        </span>
      </div>

      <div class="steps-container">
        <h3 class="steps-title">烹饪步骤</h3>
        <div
          v-for="(s, idx) in recipe.steps"
          :key="idx"
          class="step-item"
          :style="{ animationDelay: idx * 0.1 + 's' }"
        >
          <div class="step-number">
            <span>{{ s.step || idx + 1 }}</span>
          </div>
          <p class="step-text">{{ s.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed } from 'vue'
import { useFavorites } from '../composables/useFavorites.js'

const props = defineProps({
  recipe: { type: Object, default: null },
  recognizedIngredients: { type: Array, default: () => [] },
})

defineEmits(['close'])

const { isFavorite, toggleFavorite } = useFavorites()
const isFav = computed(() => isFavorite(props.recipe))

const checkedIngredients = reactive(new Set())

function toggleIngredient(ing) {
  if (checkedIngredients.has(ing)) {
    checkedIngredients.delete(ing)
  } else {
    checkedIngredients.add(ing)
  }
}

function isRecognized(name) {
  return props.recognizedIngredients.some(
    (i) => name.includes(i) || i.includes(name)
  )
}
</script>

<style scoped>
.cooking-steps-overlay {
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

.cooking-steps-panel {
  position: relative;
  background: linear-gradient(160deg, #1e1b4b 0%, #1e293b 100%);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 24px;
  padding: 36px 32px 32px;
  max-width: 600px;
  width: 100%;
  max-height: 85vh;
  overflow-y: auto;
  animation: slideUp 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.5);
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

.fav-btn-panel {
  position: absolute;
  top: 16px;
  right: 60px;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.fav-btn-panel:hover {
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
}
.fav-btn-panel.active {
  color: #fbbf24;
}

.panel-header {
  text-align: center;
  margin-bottom: 24px;
}
.panel-badge {
  display: inline-block;
  font-size: 0.75rem;
  padding: 4px 12px;
  border-radius: 20px;
  background: rgba(102, 126, 234, 0.15);
  color: #a5b4fc;
  font-weight: 500;
  margin-bottom: 12px;
}
.panel-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: #f1f5f9;
  margin: 0 0 8px;
}
.panel-desc {
  font-size: 0.92rem;
  color: #94a3b8;
  margin: 0 0 14px;
}
.panel-meta {
  display: flex;
  justify-content: center;
  gap: 20px;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: #94a3b8;
}

.ingredients-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-bottom: 28px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 14px;
}
.ing-chip {
  font-size: 0.82rem;
  padding: 5px 14px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.06);
  color: #cbd5e1;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
  user-select: none;
}
.ing-chip:hover {
  background: rgba(255, 255, 255, 0.12);
}
.ing-chip.is-main {
  background: rgba(102, 126, 234, 0.2);
  color: #c7d2fe;
  font-weight: 500;
}
.ing-chip.checked {
  background: rgba(52, 211, 153, 0.12);
  color: #6ee7b7;
  text-decoration: line-through;
  opacity: 0.7;
}
.check-box {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  flex-shrink: 0;
}
.ing-chip.checked .check-box {
  background: rgba(52, 211, 153, 0.3);
  border-color: rgba(52, 211, 153, 0.5);
}

.steps-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.75);
  margin-bottom: 20px;
}

.step-item {
  display: flex;
  gap: 16px;
  margin-bottom: 18px;
  animation: stepIn 0.5s ease both;
}
@keyframes stepIn {
  from { opacity: 0; transform: translateX(-16px); }
  to { opacity: 1; transform: translateX(0); }
}

.step-number {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #f857a6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.88rem;
  font-weight: 700;
  color: #fff;
  margin-top: 2px;
}
.step-text {
  flex: 1;
  font-size: 0.92rem;
  color: #cbd5e1;
  line-height: 1.7;
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  margin: 0;
}
</style>
