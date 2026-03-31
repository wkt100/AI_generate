<template>
  <div class="task-card" @click="$emit('click')">
    <div class="task-id">#{{ task.id }}</div>
    <div class="task-input">{{ truncatedInput }}</div>
    <div class="task-state" :class="stateClass">{{ task.current_state }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  task: {
    id: string
    user_input: string
    status: string
    current_state: string
  }
}>()

defineEmits<{
  (e: 'click'): void
}>()

const truncatedInput = computed(() => {
  const input = props.task.user_input
  return input.length > 50 ? input.substring(0, 50) + '...' : input
})

const stateClass = computed(() => {
  const state = props.task.status
  return {
    'state-init': state === 'init' || state === 'creating',
    'state-active': ['plan', 'review', 'execute', 'validate'].includes(state),
    'state-done': state === 'done',
    'state-failed': state === 'failed' || state === 'human_intervention'
  }
})
</script>

<style scoped>
.task-card {
  background: white;
  border-radius: 6px;
  padding: 12px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  transition: box-shadow 0.2s;
}
.task-card:hover {
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.task-id {
  font-size: 11px;
  color: #94a3b8;
  font-family: monospace;
}
.task-input {
  font-size: 13px;
  color: #1e293b;
  margin: 8px 0;
  line-height: 1.4;
}
.task-state {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
  display: inline-block;
}
.state-init { background: #fef3c7; color: #92400e; }
.state-active { background: #dbeafe; color: #1e40af; }
.state-done { background: #d1fae5; color: #065f46; }
.state-failed { background: #fee2e2; color: #991b1b; }
</style>
