<template>
  <div id="app" class="min-h-screen flex flex-col" style="background-color: var(--color-xuan-qing);">
    <!-- 顶部导航 -->
    <header
      class="border-b px-6 py-4 flex items-center justify-between"
      style="background-color: var(--color-xuan-qing-light); border-color: #1e293b;"
    >
      <div class="flex items-center gap-3">
        <span class="text-2xl">📜</span>
        <h1 class="text-xl font-bold tracking-wider" style="color: var(--color-amber-gold);">EDICT</h1>
      </div>
      <div class="flex items-center gap-4">
        <span class="text-sm" style="color: #94a3b8;">多智能体协同系统</span>
        <div class="flex gap-2">
          <button
            @click="currentView = 'kanban'"
            :class="[
              'px-4 py-2 rounded-lg text-sm font-medium transition-all',
              currentView === 'kanban'
                ? 'text-white'
                : 'hover:text-white'
            ]"
            :style="currentView === 'kanban' ? { backgroundColor: 'var(--color-amber-gold)', color: 'var(--color-xuan-qing)' } : { color: '#94a3b8' }"
          >
            看板
          </button>
          <button
            @click="currentView = 'dashboard'"
            :class="[
              'px-4 py-2 rounded-lg text-sm font-medium transition-all',
              currentView === 'dashboard'
                ? 'text-white'
                : 'hover:text-white'
            ]"
            :style="currentView === 'dashboard' ? { backgroundColor: 'var(--color-amber-gold)', color: 'var(--color-xuan-qing)' } : { color: '#94a3b8' }"
          >
            仪表盘
          </button>
        </div>
      </div>
    </header>

    <!-- 主内容区 - 左右分栏 -->
    <main class="flex-1 flex overflow-hidden">
      <!-- 左侧: DAG 拓扑图区域 -->
      <div class="w-2/3 border-r overflow-auto" style="border-color: #1e293b;">
        <KanbanView v-if="currentView === 'kanban'" />
        <DashboardView v-else />
      </div>

      <!-- 右侧: 流式日志终端 -->
      <div
        class="w-1/3 flex flex-col"
        style="background-color: var(--color-xuan-qing-light);"
      >
        <div
          class="px-4 py-3 border-b flex items-center justify-between"
          style="border-color: #1e293b;"
        >
          <span class="text-sm font-medium" style="color: #cbd5e1;">执行日志</span>
          <span class="text-xs" style="color: #64748b;">实时</span>
        </div>
        <div class="flex-1 overflow-auto p-4 font-mono text-sm">
          <div v-for="(log, i) in logs" :key="i" class="mb-2" style="color: #94a3b8;">
            <span class="mr-2" style="color: #475569;">[{{ log.time }}]</span>
            <span :class="logColor(log.level)">{{ log.message }}</span>
          </div>
          <div v-if="logs.length === 0" class="text-center py-8" style="color: #475569;">
            等待任务执行...
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import KanbanView from './views/KanbanView.vue'
import DashboardView from './views/DashboardView.vue'

const currentView = ref<'kanban' | 'dashboard'>('dashboard')

const logs = ref<Array<{time: string, message: string, level: string}>>([])

const logColor = (level: string) => {
  if (level === 'error') return 'text-red-500'
  if (level === 'warning') return 'text-amber-500'
  if (level === 'success') return 'text-teal-500'
  return 'text-slate-300'
}

// 添加日志的函数，供子组件调用
const addLog = (message: string, level: string = 'info') => {
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  logs.value.push({ time, message, level })
}

defineExpose({ addLog })
</script>
