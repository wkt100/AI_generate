<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>任务详情 #{{ task.id }}</h2>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <div class="modal-body">
        <div class="task-info">
          <p><strong>描述:</strong> {{ task.user_input }}</p>
          <p><strong>状态:</strong> <span :class="'status-' + task.status">{{ task.current_state }}</span></p>
        </div>

        <div class="steps-section">
          <h3>执行步骤</h3>
          <div v-for="step in steps" :key="step.id" class="step-item">
            <span class="step-name">{{ step.step_name }}</span>
            <span class="step-dept">{{ step.department }}</span>
            <span :class="'step-status ' + step.status">{{ step.status }}</span>
          </div>
        </div>

        <div class="actions">
          <button @click="downloadOutput" class="btn-primary">下载产出物</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  show: boolean
  task: any
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const steps = ref<any[]>([])

watch(() => props.task, async (newTask) => {
  if (newTask && newTask.id) {
    try {
      const res = await fetch(`/api/tasks/${newTask.id}/steps`)
      steps.value = await res.json()
    } catch (e) {
      console.error('Failed to fetch steps:', e)
    }
  }
}, { immediate: true })

const downloadOutput = async () => {
  try {
    const res = await fetch(`/api/tasks/${props.task.id}/download`)
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `task_${props.task.id}_output.zip`
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Download failed:', e)
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow: hidden;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
}
.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
}
.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #64748b;
}
.modal-body {
  padding: 20px;
  overflow-y: auto;
  max-height: calc(80vh - 60px);
}
.task-info p {
  margin-bottom: 8px;
}
.status-init, .status-creating { color: #f59e0b; }
.status-active { color: #3b82f6; }
.status-done { color: #10b981; }
.status-failed { color: #ef4444; }
.steps-section {
  margin-top: 20px;
}
.steps-section h3 {
  font-size: 14px;
  margin-bottom: 12px;
}
.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 6px;
  margin-bottom: 8px;
}
.step-name {
  flex: 1;
  font-size: 14px;
}
.step-dept {
  font-size: 12px;
  color: #64748b;
}
.step-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
}
.step-status.pending { background: #fef3c7; color: #92400e; }
.step-status.running { background: #dbeafe; color: #1e40af; }
.step-status.success { background: #d1fae5; color: #065f46; }
.step-status.failed { background: #fee2e2; color: #991b1b; }
.actions {
  margin-top: 20px;
  text-align: right;
}
.btn-primary {
  padding: 10px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}
.btn-primary:hover {
  background: #2563eb;
}
</style>
