<template>
  <div class="policy-node">
    <Handle type="target" :position="Position.Left" />
    <div class="node-content">
      <span class="node-icon">📋</span>
      <div class="node-text">
        <div class="node-label">{{ data.label }}</div>
        <div class="node-type">{{ data.type || 'Policy' }}</div>
      </div>
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
.policy-node {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
  padding: 16px 24px;
  min-width: 180px;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.12);
  color: white;
  transition: transform 0.2s, box-shadow 0.2s;
}

.policy-node:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.node-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.node-icon {
  font-size: 20px;
}

.node-text {
  flex: 1;
}

.node-label {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 2px;
}

.node-type {
  font-size: 10px;
  opacity: 0.8;
}
</style>

