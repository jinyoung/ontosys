<template>
  <div class="command-node">
    <Handle type="target" :position="Position.Left" />
    <div class="node-content">
      <span class="node-icon">⚡</span>
      <span class="node-label">{{ data.label }}</span>
      <span class="intent-badge">{{ data.intent || 'Custom' }}</span>
    </div>
    <Handle type="source" :position="Position.Right" />
  </div>
</template>

<script setup>
import { Handle, Position } from '@vue-flow/core'

defineProps({
  data: {
    type: Object,
    required: true
  }
})
</script>

<style scoped>
.command-node {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-radius: 24px;
  padding: 12px 20px;
  min-width: 160px;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.12);
  color: white;
  transition: transform 0.2s, box-shadow 0.2s;
}

.command-node:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.node-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-icon {
  font-size: 18px;
}

.node-label {
  font-size: 14px;
  font-weight: 600;
  flex: 1;
}

.intent-badge {
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 8px;
  font-size: 10px;
  font-weight: 500;
}
</style>

