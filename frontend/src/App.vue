<template>
  <div class="app">
    <header class="app-header">
      <h1>🎨 Event-Storming → Neo4j → VueFlow</h1>
      <p class="subtitle">Extract domain concepts and visualize as graph</p>
    </header>
    
    <div class="app-layout">
      <aside class="sidebar">
        <UploadPanel />
      </aside>
      
      <main class="main-content">
        <GraphCanvas v-if="store.hasData" />
        <div v-else class="empty-state">
          <div class="empty-icon">📊</div>
          <h2>No Graph Data</h2>
          <p>Upload a document and start extraction to see the graph</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { useGraphStore } from '@/stores/graphStore'
import UploadPanel from '@/components/UploadPanel.vue'
import GraphCanvas from '@/components/GraphCanvas.vue'

const store = useGraphStore()
</script>

<style scoped>
.app {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
}

.subtitle {
  margin: 4px 0 0;
  font-size: 14px;
  opacity: 0.9;
}

.app-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  width: 320px;
  background: #f8f9fa;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
  padding: 16px;
}

.main-content {
  flex: 1;
  background: white;
  position: relative;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h2 {
  margin: 0 0 8px;
  font-size: 24px;
  color: #666;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}
</style>



