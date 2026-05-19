<template>
  <div class="recipe-card" @click="$emit('select', recipe)">
    <div class="card-header">
      <h3 class="recipe-name">{{ recipe.name }}</h3>
      <div class="card-header-right">
        <button class="fav-btn" :class="{ active: isFav }" @click.stop="toggleFavorite(recipe)" :title="isFav ? '取消收藏' : '收藏'">
          <svg width="16" height="16" viewBox="0 0 24 24" :fill="isFav ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
          </svg>
        </button>
        <div class="badges">
        <span class="badge difficulty" :class="recipe.difficulty">
          {{ recipe.difficulty || '未知' }}
        </span>
        <span class="badge time">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
          {{ recipe.cooking_time || '未知' }}
        </span>
      </div>
      </div>
    </div>

    <p class="recipe-desc">{{ recipe.description }}</p>

    <div class="ingredients-needed">
      <span class="label">所需食材：</span>
      <span
        v-for="(ing, idx) in recipe.ingredients_needed"
        :key="idx"
        class="mini-tag"
        :class="{ highlight: isRecognized(ing) }"
      >
        {{ ing }}
      </span>
    </div>

    <div class="card-footer">
      <span class="step-count">共 {{ recipe.steps?.length || 0 }} 步</span>
      <span class="view-detail">
        查看做法
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useFavorites } from '../composables/useFavorites.js'

const props = defineProps({
  recipe: { type: Object, required: true },
  recognizedIngredients: { type: Array, default: () => [] },
})

defineEmits(['select'])

const { isFavorite, toggleFavorite } = useFavorites()
const isFav = computed(() => isFavorite(props.recipe))

function isRecognized(name) {
  return props.recognizedIngredients.some(
    (i) => name.includes(i) || i.includes(name)
  )
}
</script>

<style scoped>
.recipe-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 18px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
}
.recipe-card:hover {
  transform: translateY(-4px);
  border-color: rgba(102, 126, 234, 0.4);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}
.recipe-name {
  font-size: 1.2rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
}

.card-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.fav-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.06);
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}
.fav-btn:hover {
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
}
.fav-btn.active {
  color: #fbbf24;
}

.badges {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
.badge {
  font-size: 0.75rem;
  padding: 4px 10px;
  border-radius: 20px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}
.difficulty {
  background: rgba(102, 126, 234, 0.15);
  color: #a5b4fc;
}
.difficulty.简单 {
  background: rgba(52, 211, 153, 0.15);
  color: #6ee7b7;
}
.difficulty.中等 {
  background: rgba(251, 191, 36, 0.15);
  color: #fcd34d;
}
.difficulty.困难 {
  background: rgba(248, 113, 113, 0.15);
  color: #fca5a5;
}
.time {
  background: rgba(255, 255, 255, 0.06);
  color: #94a3b8;
}

.recipe-desc {
  font-size: 0.9rem;
  color: #94a3b8;
  margin: 0 0 16px;
  line-height: 1.5;
}

.ingredients-needed {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-bottom: 18px;
}
.label {
  font-size: 0.8rem;
  color: #64748b;
  margin-right: 4px;
}
.mini-tag {
  font-size: 0.78rem;
  padding: 3px 10px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.06);
  color: #cbd5e1;
}
.mini-tag.highlight {
  background: rgba(102, 126, 234, 0.2);
  color: #a5b4fc;
  font-weight: 500;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}
.step-count {
  font-size: 0.82rem;
  color: #64748b;
}
.view-detail {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.88rem;
  font-weight: 500;
  color: #818cf8;
  transition: gap 0.2s;
}
.recipe-card:hover .view-detail {
  gap: 8px;
}
</style>
