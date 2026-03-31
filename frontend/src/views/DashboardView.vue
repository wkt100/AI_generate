<template>
  <div class="dashboard-view h-full flex flex-col">
    <!-- 任务输入区 -->
    <div class="mb-6">
      <TaskInput @submit="onSubmitTask" />
    </div>

    <!-- 任务卡片列表 -->
    <div v-if="!currentTask" class="mb-6">
      <div class="text-sm text-slate-400 mb-3">最近任务</div>
      <div class="space-y-2">
        <div
          v-for="task in recentTasks"
          :key="task.id"
          @click="selectTask(task)"
          class="card cursor-pointer hover:border-amber-gold/50 transition-colors"
        >
          <div class="flex items-center justify-between">
            <div>
              <span class="text-xs text-slate-500 font-mono">#{{ task.id }}</span>
              <div class="text-slate-200 mt-1">{{ task.user_input }}</div>
            </div>
            <span :class="['px-3 py-1 rounded-full text-xs font-medium', statusClass(task.status)]">
              {{ task.current_state }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 选中任务的 DAG + 日志 -->
    <div v-if="currentTask" class="flex-1 flex gap-4 min-h-0">
      <!-- DAG 图 -->
      <div class="flex-1 card min-h-0 overflow-hidden">
        <div class="flex items-center justify-between mb-3">
          <div>
            <span class="text-sm text-slate-400">任务 #</span>
            <span class="text-slate-300 font-mono">{{ currentTask.id }}</span>
          </div>
          <button @click="currentTask = null" class="text-slate-500 hover:text-slate-300">×</button>
        </div>
        <DagGraph
          :dag="dagData"
          :task-steps="taskSteps"
          class="h-[calc(100%-3rem)]"
        />
      </div>

      <!-- 日志终端 -->
      <div class="w-96 card min-h-0 overflow-hidden">
        <StreamingLog ref="logComponent" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import TaskInput from '../components/TaskInput.vue'
import DagGraph from '../components/DagGraph.vue'
import StreamingLog from '../components/StreamingLog.vue'

const recentTasks = ref<any[]>([])
const currentTask = ref<any>(null)
const taskSteps = ref<any[]>([])
const dagData = ref<{nodes: any[], edges: any[]}>({nodes: [], edges: []})
const logComponent = ref<InstanceType<typeof StreamingLog> | null>(null)
const ws = ref<WebSocket | null>(null)

const statusClass = (status: string) => {
  const classes: Record<string, string> = {
    'init': 'bg-amber-500/20 text-amber-400',
    'plan': 'bg-amber-500/20 text-amber-400',
    'review': 'bg-amber-500/20 text-amber-400',
    'execute': 'bg-blue-500/20 text-blue-400',
    'validate': 'bg-blue-500/20 text-blue-400',
    'done': 'bg-green-500/20 text-green-400',
    'failed': 'bg-red-500/20 text-red-400'
  }
  return classes[status] || 'bg-slate-500/20 text-slate-400'
}

const fetchTasks = async () => {
  try {
    const res = await fetch('/api/tasks')
    recentTasks.value = await res.json()
  } catch (e) {
    console.error('Failed to fetch tasks:', e)
  }
}

const selectTask = async (task: any) => {
  currentTask.value = task

  // 获取任务步骤
  try {
    const res = await fetch(`/api/tasks/${task.id}/steps`)
    taskSteps.value = await res.json()
  } catch (e) {
    console.error('Failed to fetch steps:', e)
  }

  // 解析 DAG
  if (task.dag_definition) {
    try {
      dagData.value = JSON.parse(task.dag_definition)
    } catch (e) {
      console.error('Failed to parse DAG:', e)
    }
  }

  // 连接 WebSocket 获取实时日志
  connectWebSocket(task.id)
}

const connectWebSocket = (taskId: string) => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.hostname
  ws.value = new WebSocket(`${protocol}//${host}:8000/ws/tasks/${taskId}`)

  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data)

    // 映射 WebSocket 消息到日志
    const agentMap: Record<string, string> = {
      'INIT': '系统',
      'PLAN': '中书省',
      'REVIEW': '门下省',
      'EXECUTE': '尚书省/六部',
      'VALIDATE': '刑部',
      'DONE': '系统'
    }

    const agent = agentMap[data.current_state] || '系统'
    let message = ''

    if (data.step) {
      message = `[${data.step}] ${data.department || ''} 执行中...`
    } else if (data.message) {
      message = data.message
    } else if (data.status === 'done') {
      message = '任务完成！'
    }

    logComponent.value?.addLog(agent, message, data.status === 'failed' ? 'error' : 'info')

    // 更新任务状态
    if (currentTask.value?.id === taskId) {
      currentTask.value.status = data.status
      currentTask.value.current_state = data.current_state
    }
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
    recentTasks.value.unshift(task)
    selectTask(task)
  } catch (e) {
    console.error('Failed to create task:', e)
  }
}

onMounted(() => {
  fetchTasks()
})

onUnmounted(() => {
  if (ws.value) {
    ws.value.close()
  }
})
</script>
