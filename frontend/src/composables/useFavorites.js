import { ref, watch } from 'vue'

const STORAGE_KEY = 'chuling_favorites'
const favorites = ref(loadFavorites())

function loadFavorites() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

function saveFavorites() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(favorites.value))
}

export function useFavorites() {
  function isFavorite(recipe) {
    return favorites.value.some((f) => f.name === recipe.name)
  }

  function toggleFavorite(recipe) {
    const idx = favorites.value.findIndex((f) => f.name === recipe.name)
    if (idx >= 0) {
      favorites.value.splice(idx, 1)
    } else {
      favorites.value.push({
        name: recipe.name,
        description: recipe.description,
        difficulty: recipe.difficulty,
        cooking_time: recipe.cooking_time,
        ingredients_needed: recipe.ingredients_needed || [],
        steps: recipe.steps || [],
      })
    }
    saveFavorites()
  }

  return { favorites, isFavorite, toggleFavorite }
}
