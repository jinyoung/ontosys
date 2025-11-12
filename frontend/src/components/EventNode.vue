<template>
  <div class="event-node">
    <Handle type="target" :position="Position.Left" />
    <Handle type="target" :position="Position.Top" />
    <div class="node-content">
      <span class="node-icon">🎯</span>
      <span class="node-label">{{ data.label }}</span>
    </div>
    <Handle type="source" :position="Position.Right" />
    <Handle type="source" :position="Position.Bottom" />
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
.event-node {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  border-radius: 8px;
  padding: 14px 18px;
  min-width: 140px;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.12);
  color: #333;
  transform: rotate(45deg);
  transition: transform 0.2s, box-shadow 0.2s;
}

.event-node:hover {
  transform: rotate(45deg) scale(1.08);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.node-content {
  transform: rotate(-45deg);
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: center;
}

.node-icon {
  font-size: 16px;
}

.node-label {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}
</style>

