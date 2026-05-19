<template>
  <div class="image-upload">
    <div
      class="upload-zone"
      :class="{ 'is-dragover': isDragover, 'has-image': previewUrl }"
      @dragover.prevent="isDragover = true"
      @dragleave.prevent="isDragover = false"
      @drop.prevent="handleDrop"
      @click="triggerInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept="image/jpeg,image/png,image/gif,image/webp"
        hidden
        @change="handleFileChange"
      />

      <div v-if="!previewUrl" class="upload-prompt">
        <div class="upload-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
            <circle cx="8.5" cy="8.5" r="1.5" />
            <polyline points="21 15 16 10 5 21" />
          </svg>
        </div>
        <p class="upload-text">拖拽食材图片到这里</p>
        <p class="upload-hint">或点击此区域选择图片</p>
        <p class="upload-limit">支持 JPG / PNG / GIF / WebP，最大 10MB</p>
      </div>

      <div v-else class="image-preview">
        <img :src="previewUrl" alt="预览" />
        <button class="btn-reset" @click.stop="resetUpload">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
    </div>

    <button
      v-if="previewUrl && !loading"
      class="btn-analyze"
      @click="analyze"
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
      </svg>
      开始智能分析
    </button>

    <div v-if="loading" class="loading-box">
      <div class="spinner"></div>
      <p class="loading-text">AI 正在识别食材并生成菜谱...</p>
    </div>

    <p v-if="error" class="error-msg">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { uploadAndAnalyze } from '../api/index.js'

const emit = defineEmits(['uploaded'])

const fileInput = ref(null)
const previewUrl = ref('')
const isDragover = ref(false)
const loading = ref(false)
const error = ref('')
const selectedFile = ref(null)

function triggerInput() {
  if (previewUrl.value) return
  fileInput.value?.click()
}

function handleFileChange(e) {
  const file = e.target.files?.[0]
  if (file) setFile(file)
}

function handleDrop(e) {
  isDragover.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) setFile(file)
}

function setFile(file) {
  error.value = ''
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    error.value = '不支持该图片格式，请上传 JPG/PNG/GIF/WebP 格式'
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    error.value = '图片大小不能超过 10MB'
    return
  }
  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
}

function resetUpload() {
  previewUrl.value = ''
  selectedFile.value = null
  error.value = ''
  if (fileInput.value) fileInput.value.value = ''
}

async function analyze() {
  if (!selectedFile.value) return
  loading.value = true
  error.value = ''
  try {
    const result = await uploadAndAnalyze(selectedFile.value)
    emit('uploaded', result)
  } catch (e) {
    error.value = e.message || '分析失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.image-upload {
  margin-bottom: 32px;
}

.upload-zone {
  position: relative;
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.35s ease;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(12px);
  overflow: hidden;
}
.upload-zone:hover {
  border-color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.06);
}
.upload-zone.is-dragover {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.12);
  transform: scale(1.01);
}
.upload-zone.has-image {
  padding: 12px;
  border-style: solid;
  border-color: rgba(255, 255, 255, 0.15);
}

.upload-prompt {
  pointer-events: none;
}
.upload-icon {
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 16px;
}
.upload-text {
  font-size: 1.15rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 8px;
}
.upload-hint {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 12px;
}
.upload-limit {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.25);
}

.image-preview {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
}
.image-preview img {
  display: block;
  width: 100%;
  max-height: 360px;
  object-fit: contain;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 14px;
}
.btn-reset {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  backdrop-filter: blur(8px);
}
.btn-reset:hover {
  background: rgba(239, 68, 68, 0.8);
}

.btn-analyze {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  margin-top: 16px;
  padding: 16px 32px;
  font-size: 1.1rem;
  font-weight: 600;
  font-family: inherit;
  color: #fff;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  background: linear-gradient(135deg, #667eea 0%, #f857a6 100%);
  transition: all 0.3s ease;
  letter-spacing: 1px;
}
.btn-analyze:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
}
.btn-analyze:active {
  transform: translateY(0);
}

.loading-box {
  text-align: center;
  margin-top: 24px;
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
  font-size: 0.9rem;
}

.error-msg {
  margin-top: 12px;
  text-align: center;
  color: #f87171;
  font-size: 0.88rem;
  padding: 12px 16px;
  background: rgba(248, 113, 113, 0.1);
  border-radius: 10px;
  border: 1px solid rgba(248, 113, 113, 0.2);
}
</style>
