<template>
  <div class="aggregate-node">
    <div class="node-header">
      <span class="node-icon">📦</span>
      <span class="node-title">{{ data.label }}</span>
    </div>
    <div class="node-body">
      <p class="node-description">{{ truncate(data.description) }}</p>
      <div class="node-footer">
        <span class="confidence-badge" :class="confidenceClass">
          {{ (data.confidence * 100).toFixed(0) }}%
        </span>
        <span v-if="data.tags && data.tags.length" class="tags">
          <span v-for="tag in data.tags" :key="tag" class="tag">{{ tag }}</span>
        </span>
      </div>
    </div>
    <Handle type="target" :position="Position.Top" />
    <Handle type="source" :position="Position.Bottom" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

const confidenceClass = computed(() => {
  const conf = props.data.confidence || 0
  if (conf >= 0.8) return 'high'
  if (conf >= 0.6) return 'medium'
  return 'low'
})

const truncate = (text, maxLength = 60) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}
</script>

<style scoped>
.aggregate-node {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 16px;
  min-width: 200px;
  max-width: 280px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  color: white;
  transition: transform 0.2s, box-shadow 0.2s;
}

.aggregate-node:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
}

.node-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.node-icon {
  font-size: 24px;
}

.node-title {
  font-size: 16px;
  font-weight: 600;
}

.node-body {
  font-size: 13px;
}

.node-description {
  margin-bottom: 8px;
  opacity: 0.9;
  line-height: 1.4;
}

.node-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.confidence-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.2);
}

.confidence-badge.high {
  background: rgba(76, 175, 80, 0.8);
}

.confidence-badge.medium {
  background: rgba(255, 193, 7, 0.8);
}

.confidence-badge.low {
  background: rgba(244, 67, 54, 0.8);
}

.tags {
  display: flex;
  gap: 4px;
}

.tag {
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  font-size: 10px;
}
</style>

