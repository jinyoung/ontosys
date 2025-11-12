<template>
  <div class="upload-panel">
    <h2>📄 Upload Document</h2>
    
    <div v-if="!store.currentDocId" class="upload-area">
      <input
        ref="fileInput"
        type="file"
        accept=".pdf,.docx,.doc,.txt"
        @change="handleFileSelect"
        class="file-input"
      />
      <button @click="$refs.fileInput.click()" class="upload-button">
        Choose File
      </button>
      <p class="help-text">Support: PDF, DOCX, TXT</p>
    </div>
    
    <div v-else class="doc-info">
      <p><strong>Document ID:</strong> {{ store.currentDocId }}</p>
      
      <div v-if="store.extractionStatus === null" class="action-section">
        <button @click="startExtraction" class="primary-button" :disabled="store.isLoading">
          🚀 Start Extraction
        </button>
      </div>
      
      <div v-else class="status-section">
        <p><strong>Status:</strong> 
          <span :class="`status-${store.extractionStatus}`">
            {{ store.extractionStatus }}
          </span>
        </p>
        
        <div v-if="store.extractionStatus === 'done'" class="stats">
          <p>✅ Extraction completed!</p>
          <p>Nodes: {{ store.nodeCount }}</p>
          <p>Edges: {{ store.edgeCount }}</p>
        </div>
      </div>
      
      <button @click="reset" class="secondary-button">
        Reset
      </button>
    </div>
    
    <div v-if="store.error" class="error-message">
      {{ store.error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useGraphStore } from '@/stores/graphStore'

const store = useGraphStore()
const fileInput = ref(null)

async function handleFileSelect(event) {
  const file = event.target.files[0]
  if (!file) return
  
  try {
    await store.uploadDocument(file)
  } catch (err) {
    console.error('Upload failed:', err)
  }
}

async function startExtraction() {
  try {
    await store.startExtraction()
  } catch (err) {
    console.error('Extraction failed:', err)
  }
}

function reset() {
  store.reset()
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>

<style scoped>
.upload-panel {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-bottom: 16px;
  font-size: 18px;
  color: #333;
}

.upload-area {
  text-align: center;
}

.file-input {
  display: none;
}

.upload-button {
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.upload-button:hover {
  background: #5568d3;
}

.help-text {
  margin-top: 8px;
  font-size: 12px;
  color: #666;
}

.doc-info {
  font-size: 14px;
}

.doc-info p {
  margin-bottom: 8px;
}

.action-section {
  margin: 16px 0;
}

.primary-button {
  padding: 10px 20px;
  background: #4facfe;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.primary-button:hover:not(:disabled) {
  background: #3a98e8;
}

.primary-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.secondary-button {
  padding: 8px 16px;
  background: #f0f0f0;
  color: #333;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  margin-top: 12px;
}

.secondary-button:hover {
  background: #e0e0e0;
}

.status-section {
  margin: 16px 0;
}

.status-queued,
.status-running {
  color: #ff9800;
  font-weight: 600;
}

.status-done {
  color: #4caf50;
  font-weight: 600;
}

.status-error {
  color: #f44336;
  font-weight: 600;
}

.stats {
  margin-top: 12px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 6px;
}

.stats p {
  margin: 4px 0;
}

.error-message {
  margin-top: 12px;
  padding: 12px;
  background: #ffebee;
  color: #c62828;
  border-radius: 6px;
  font-size: 13px;
}
</style>



