<template>
  <div id="app">
    <header>
      <h1>Edict - 多Agent执行系统</h1>
      <div class="view-toggle">
        <button :class="{ active: currentView === 'kanban' }" @click="currentView = 'kanban'">看板</button>
        <button :class="{ active: currentView === 'dashboard' }" @click="currentView = 'dashboard'">仪表盘</button>
      </div>
    </header>
    <main>
      <KanbanView v-if="currentView === 'kanban'" />
      <DashboardView v-else />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import KanbanView from './views/KanbanView.vue'
import DashboardView from './views/DashboardView.vue'

const currentView = ref<'kanban' | 'dashboard'>('kanban')
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: #f8fafc;
  color: #1e293b;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #1e293b;
  color: white;
}
header h1 {
  font-size: 20px;
  font-weight: 700;
}
.view-toggle {
  display: flex;
  gap: 8px;
}
.view-toggle button {
  padding: 8px 16px;
  background: transparent;
  color: #94a3b8;
  border: 1px solid #475569;
  border-radius: 6px;
  cursor: pointer;
}
.view-toggle button.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}
#app main {
  min-height: calc(100vh - 70px);
}
</style>
