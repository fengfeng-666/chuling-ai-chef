const BASE_URL = '/api'

export async function uploadAndAnalyze(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${BASE_URL}/analyze`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail || `请求失败 (${response.status})`)
  }

  return response.json()
}

export async function quizRecommend(answers) {
  const response = await fetch(`${BASE_URL}/quiz-recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answers }),
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail || `请求失败 (${response.status})`)
  }

  return response.json()
}

export async function sendMessage(message, imageFile, history = null) {
  const formData = new FormData()
  formData.append('message', message || '')
  if (imageFile) {
    formData.append('file', imageFile)
  }
  if (history && history.length > 0) {
    formData.append('history_json', JSON.stringify(history))
  }

  const response = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail || `请求失败 (${response.status})`)
  }

  return response.json()
}

export function sendMessageStream({
  message,
  imageFile,
  history,
  token,
  sessionId,
  signal,
  onText,
  onRecipes,
  onDone,
  onError,
}) {
  const formData = new FormData()
  formData.append('message', message || '')
  if (imageFile) formData.append('file', imageFile)
  if (history && history.length > 0) formData.append('history_json', JSON.stringify(history))
  if (sessionId) formData.append('session_id', String(sessionId))

  const headers = {}
  if (token) headers['Authorization'] = `Bearer ${token}`

  fetch('/api/chat/stream', {
    method: 'POST',
    body: formData,
    headers,
    signal,
  })
    .then(async (response) => {
      if (!response.ok) {
        const data = await response.json().catch(() => ({}))
        throw new Error(data.detail || `请求失败 (${response.status})`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      function readNext() {
        reader.read().then(({ done, value }) => {
          if (done) {
            if (buffer.trim()) {
              const trimmed = buffer.trim()
              if (trimmed.startsWith('data: ')) {
                let parsed
                try { parsed = JSON.parse(trimmed.slice(6)) } catch { return }
                switch (parsed.type) {
                  case 'text': onText?.(parsed.content); break
                  case 'recipes': onRecipes?.({ recipes: parsed.recipes || [], ingredients: parsed.ingredients || [] }); break
                  case 'done': onDone?.(parsed.session_id || null); break
                  case 'error': onError?.(parsed.message || '未知错误'); break
                }
              }
            }
            return
          }

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            const trimmed = line.trim()
            if (!trimmed.startsWith('data: ')) continue

            let parsed
            try { parsed = JSON.parse(trimmed.slice(6)) } catch { continue }

            switch (parsed.type) {
              case 'text': onText?.(parsed.content); break
              case 'recipes': onRecipes?.({ recipes: parsed.recipes || [], ingredients: parsed.ingredients || [] }); break
              case 'done': onDone?.(parsed.session_id || null); break
              case 'error': onError?.(parsed.message || '未知错误'); break
            }
          }

          readNext()
        }).catch((err) => {
          if (err.name === 'AbortError') return
          onError?.(err.message || '连接中断')
        })
      }

      readNext()
    })
    .catch((err) => {
      if (err.name === 'AbortError') return
      onError?.(err.message || '网络请求失败')
    })
}

export async function lookupDishRecipe(dishName) {
  const response = await fetch(`${BASE_URL}/quiz-recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      answers: { '想吃': dishName, '菜系偏好': '不限', '口味偏好': '不限' },
    }),
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail || `请求失败 (${response.status})`)
  }

  return response.json()
}
