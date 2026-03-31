<template>
  <div class="kanban-view">
    <TaskInput @submit="onSubmitTask" />
    <div class="kanban-board">
      <KanbanColumn
        v-for="column in columns"
        :key="column.state"
        :title="column.title"
        :tasks="getTasksByState(column.state)"
        @select-task="onSelectTask"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import KanbanColumn from '../components/KanbanColumn.vue'
import TaskInput from '../components/TaskInput.vue'

const tasks = ref<any[]>([])
const ws = ref<WebSocket | null>(null)

const columns = [
  { title: '初始化', state: 'init' },
  { title: '规划中', state: 'plan' },
  { title: '审核中', state: 'review' },
  { title: '执行中', state: 'execute' },
  { title: '验证中', state: 'validate' },
  { title: '已完成', state: 'done' },
]

const getTasksByState = (state: string) => {
  return tasks.value.filter(t => t.status === state)
}

const fetchTasks = async () => {
  try {
    const res = await fetch('/api/tasks')
    tasks.value = await res.json()
  } catch (e) {
    console.error('Failed to fetch tasks:', e)
  }
}

const onSubmitTask = async (description: string) => {
  try {
    const res = await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_input: description })
    })
    const task = await res.json()
    tasks.value.push(task)
  } catch (e) {
    console.error('Failed to create task:', e)
  }
}

const onSelectTask = (task: any) => {
  console.log('Selected task:', task)
}

const connectWebSocket = (taskId: string) => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//localhost:8000/ws/tasks/${taskId}`
  ws.value = new WebSocket(wsUrl)
  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data)
    const task = tasks.value.find(t => t.id === data.task_id)
    if (task) {
      task.status = data.status
      task.current_state = data.current_state
    }
  }
  ws.value.onclose = () => {
    console.log(`WebSocket closed for task ${taskId}`)
  }
}

onMounted(async () => {
  await fetchTasks()
  // Connect WebSocket for each existing task
  tasks.value.forEach(t => {
    if (t.status !== 'done' && t.status !== 'failed') {
      connectWebSocket(t.id)
    }
  })
})

onUnmounted(() => {
  if (ws.value) {
    ws.value.close()
  }
})
</script>

<style scoped>
.kanban-view {
  padding: 20px;
}
.kanban-board {
  display: flex;
  gap: 16px;
  overflow-x: auto;
}
</style>
