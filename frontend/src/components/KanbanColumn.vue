<template>
  <div class="kanban-column">
    <div class="column-header">
      <h3>{{ title }}</h3>
      <span class="count">{{ tasks.length }}</span>
    </div>
    <div class="column-content">
      <TaskCard
        v-for="task in tasks"
        :key="task.id"
        :task="task"
        @click="$emit('select-task', task)"
      />
      <div v-if="tasks.length === 0" class="empty-state">
        暂无任务
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import TaskCard from './TaskCard.vue'

defineProps<{
  title: string
  tasks: any[]
}>()

defineEmits<{
  (e: 'select-task', task: any): void
}>()
</script>

<style scoped>
.kanban-column {
  background: #f1f5f9;
  border-radius: 8px;
  padding: 12px;
  min-width: 250px;
  flex: 1;
}
.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.column-header h3 {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}
.count {
  background: #e2e8f0;
  color: #64748b;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
}
.column-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.empty-state {
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
  padding: 20px;
}
</style>
