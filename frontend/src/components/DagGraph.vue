<template>
  <div class="dag-graph h-full">
    <VueFlow
      v-if="nodes.length > 0"
      :nodes="nodes"
      :edges="edges"
      :default-viewport="{ zoom: 1 }"
      fit-view-on-init
      class="bg-xuan-qing"
    >
      <Background pattern-color="#1e293b" :gap="20" />
      <Controls position="bottom-right" />

      <!-- 自定义节点样式 -->
      <template #node-default="{ data }">
        <div
          class="dag-node px-4 py-3 rounded-lg border-2 min-w-[120px] text-center transition-all duration-500"
          :class="[nodeStatusClass(data.status), 'border-' + nodeColor(data.department)]"
        >
          <div class="text-2xl mb-1">{{ departmentIcon(data.department) }}</div>
          <div class="text-sm font-medium text-slate-200">{{ data.label }}</div>
          <div class="text-xs text-slate-400 mt-1">{{ data.department }}</div>
          <div v-if="data.status === 'running'" class="mt-2">
            <div class="h-1 bg-slate-700 rounded overflow-hidden">
              <div class="h-full bg-amber-gold animate-pulse" style="width: 60%"></div>
            </div>
          </div>
        </div>
      </template>
    </VueFlow>

    <div v-else class="h-full flex items-center justify-center text-slate-500">
      <div class="text-center">
        <div class="text-4xl mb-4">🗺️</div>
        <div>等待中书省生成 DAG...</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'

const props = defineProps<{
  dag: {
    nodes: Array<{
      id: string
      name: string
      department: string
      description?: string
    }>
    edges: Array<{
      from_node: string
      to_node: string
    }>
  }
  taskSteps: Array<{
    id: string
    step_name: string
    department: string
    status: string
  }>
}>()

// 将 DAG 数据转换为 Vue Flow 格式
const nodes = computed(() => {
  if (!props.dag?.nodes) return []

  // 为节点计算位置 (简单的层级布局)
  const levels: Record<string, number> = {}
  const inDegree: Record<string, number> = {}

  // 初始化
  props.dag.nodes.forEach(n => {
    inDegree[n.id] = 0
    levels[n.id] = 0
  })

  // 计算入度
  props.dag.edges?.forEach(e => {
    inDegree[e.to_node]++
  })

  // BFS 计算层级
  const queue: string[] = []
  props.dag.nodes.forEach(n => {
    if (inDegree[n.id] === 0) {
      queue.push(n.id)
      levels[n.id] = 0
    }
  })

  while (queue.length > 0) {
    const curr = queue.shift()!
    props.dag.edges?.forEach(e => {
      if (e.from_node === curr) {
        levels[e.to_node] = Math.max(levels[e.to_node], levels[curr] + 1)
        if (!queue.includes(e.to_node)) {
          queue.push(e.to_node)
        }
      }
    })
  }

  // 按层级分组
  const levelGroups: Record<number, string[]> = {}
  props.dag.nodes.forEach(n => {
    const lv = levels[n.id]
    if (!levelGroups[lv]) levelGroups[lv] = []
    levelGroups[lv].push(n.id)
  })

  // 计算节点位置
  const nodePositions: Record<string, {x: number, y: number}> = {}
  Object.entries(levelGroups).forEach(([lv, ids]) => {
    const level = parseInt(lv)
    ids.forEach((id, idx) => {
      const count = ids.length
      nodePositions[id] = {
        x: 200 + level * 250,
        y: 150 + (idx - count / 2) * 100
      }
    })
  })

  return props.dag.nodes.map(n => {
    const step = props.taskSteps.find(s => s.step_name === n.name)
    return {
      id: n.id,
      type: 'default',
      position: nodePositions[n.id] || { x: 0, y: 0 },
      data: {
        label: n.name,
        department: n.department,
        status: step?.status || 'pending'
      }
    }
  })
})

const edges = computed(() => {
  if (!props.dag?.edges) return []
  return props.dag.edges.map((e, idx) => ({
    id: `e${idx}`,
    source: e.from_node,
    target: e.to_node,
    animated: true,
    style: { stroke: '#0D9488', strokeWidth: 2 }
  }))
})

const nodeColor = (dept: string) => {
  const colors: Record<string, string> = {
    '吏部': 'amber-gold',
    '户部': 'amber-gold',
    '礼部': 'amber-gold',
    '兵部': 'zhu-sha',
    '刑部': 'liu-li',
    '工部': 'amber-gold'
  }
  return colors[dept] || 'slate'
}

const nodeStatusClass = (status: string) => {
  if (status === 'running') return 'bg-xuan-qing-light shadow-lg shadow-amber-gold/20'
  if (status === 'success') return 'bg-liu-li/10'
  if (status === 'failed') return 'bg-zhu-sha/10'
  return 'bg-xuan-qing-light'
}

const departmentIcon = (dept: string) => {
  const icons: Record<string, string> = {
    '吏部': '⚙️',
    '户部': '💾',
    '礼部': '🎨',
    '兵部': '⚡',
    '刑部': '🛡️',
    '工部': '🔨'
  }
  return icons[dept] || '📦'
}
</script>

<style scoped>
.vue-flow {
  background-color: var(--color-xuan-qing, #121212);
}
.vue-flow__node {
  cursor: pointer;
}
</style>
