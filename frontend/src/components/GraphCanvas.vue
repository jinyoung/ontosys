<template>
  <div class="graph-canvas">
    <div class="toolbar">
      <button @click="saveGraph" :disabled="!store.isDirty || store.isLoading" class="save-button">
        💾 Save
        <span v-if="store.isDirty" class="dirty-indicator">●</span>
      </button>
      <button @click="fitView" class="tool-button">
        🎯 Fit View
      </button>
      <button @click="toggleLayout" class="tool-button">
        📐 Layout
      </button>
    </div>
    
    <VueFlow
      v-model:nodes="store.nodes"
      v-model:edges="store.edges"
      :node-types="nodeTypes"
      @nodes-change="onNodesChange"
      @edges-change="onEdgesChange"
      class="vue-flow-container"
    >
      <Background />
      <Controls />
      <MiniMap />
    </VueFlow>
  </div>
</template>

<script setup>
import { ref, markRaw } from 'vue'
import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import { useGraphStore } from '@/stores/graphStore'

import AggregateNode from './AggregateNode.vue'
import CommandNode from './CommandNode.vue'
import EventNode from './EventNode.vue'
import PolicyNode from './PolicyNode.vue'

import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

const store = useGraphStore()

// Register custom node types
const nodeTypes = {
  aggregate: markRaw(AggregateNode),
  command: markRaw(CommandNode),
  event: markRaw(EventNode),
  policy: markRaw(PolicyNode)
}

function onNodesChange(changes) {
  // Handle node changes
  console.log('Nodes changed:', changes)
}

function onEdgesChange(changes) {
  // Handle edge changes
  console.log('Edges changed:', changes)
}

async function saveGraph() {
  try {
    await store.saveGraph()
    alert('Graph saved successfully!')
  } catch (err) {
    alert('Failed to save graph: ' + err.message)
  }
}

function fitView() {
  // TODO: Implement fit view
  console.log('Fit view')
}

function toggleLayout() {
  // TODO: Implement auto layout
  console.log('Toggle layout')
}
</script>

<style scoped>
.graph-canvas {
  width: 100%;
  height: 100%;
  position: relative;
}

.toolbar {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 10;
  display: flex;
  gap: 8px;
  background: white;
  padding: 8px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.save-button {
  padding: 8px 16px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}

.save-button:hover:not(:disabled) {
  background: #45a049;
}

.save-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dirty-indicator {
  color: #ff5722;
  margin-left: 4px;
}

.tool-button {
  padding: 8px 12px;
  background: #f0f0f0;
  color: #333;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.tool-button:hover {
  background: #e0e0e0;
}

.vue-flow-container {
  width: 100%;
  height: 100%;
}
</style>

