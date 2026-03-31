<template>
  <div class="task-input">
    <textarea
      v-model="taskDescription"
      placeholder="输入任务描述，例如：写一个 Python 计算器程序"
      rows="3"
    />
    <button @click="submitTask" :disabled="!taskDescription.trim() || loading">
      {{ loading ? '执行中...' : '开始执行' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  (e: 'submit', description: string): void
}>()

const taskDescription = ref('')
const loading = ref(false)

const submitTask = async () => {
  if (!taskDescription.value.trim()) return
  loading.value = true
  emit('submit', taskDescription.value)
}
</script>

<style scoped>
.task-input {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}
.task-input textarea {
  flex: 1;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
}
.task-input textarea:focus {
  outline: none;
  border-color: #3b82f6;
}
.task-input button {
  padding: 12px 24px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.task-input button:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}
</style>
