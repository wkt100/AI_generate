<template>
  <div class="streaming-log h-full flex flex-col font-mono text-sm">
    <div class="px-4 py-3 border-b border-slate-800 flex items-center justify-between bg-xuan-qing-light">
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-liu-li animate-pulse"></span>
        <span class="text-slate-300 text-sm">终端</span>
      </div>
      <button @click="clearLogs" class="text-slate-500 hover:text-slate-300 text-xs">清除</button>
    </div>

    <div ref="logContainer" class="flex-1 overflow-auto p-4 space-y-1">
      <div
        v-for="(log, i) in logs"
        :key="i"
        class="log-line animate-fadeIn"
      >
        <span class="text-slate-600 mr-2">[{{ log.time }}]</span>
        <span :class="['agent-name mr-2', agentColor(log.agent)]">{{ log.agent }}</span>
        <span :class="logLevelColor(log.level)">{{ log.message }}</span>
      </div>

      <div v-if="logs.length === 0" class="text-slate-600 text-center py-8">
        <div class="text-2xl mb-2">⏳</div>
        <div class="text-sm">等待任务开始...</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'

interface LogEntry {
  time: string
  agent: string
  message: string
  level: 'info' | 'success' | 'error' | 'warning'
}

const logs = ref<LogEntry[]>([])
const logContainer = ref<HTMLElement | null>(null)

const agentColor = (agent: string) => {
  if (agent.includes('中书省')) return 'text-liu-li'
  if (agent.includes('门下省')) return 'text-amber-gold'
  if (agent.includes('尚书省')) return 'text-amber-gold'
  if (agent.includes('工部')) return 'text-amber-gold'
  if (agent.includes('刑部')) return 'text-zhu-sha'
  return 'text-slate-400'
}

const logLevelColor = (level: string) => {
  if (level === 'error') return 'text-zhu-sha'
  if (level === 'warning') return 'text-amber-gold'
  if (level === 'success') return 'text-liu-li'
  return 'text-slate-300'
}

const addLog = (agent: string, message: string, level: 'info' | 'success' | 'error' | 'warning' = 'info') => {
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  logs.value.push({ time, agent, message, level })

  // 自动滚动到底部
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
}

const clearLogs = () => {
  logs.value = []
}

defineExpose({ addLog })
</script>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}
</style>
