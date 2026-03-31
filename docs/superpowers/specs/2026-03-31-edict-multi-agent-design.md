# Edict 多 Agent 协同执行系统 - 设计文档

## 1. 项目概述

### 1.1 项目名称
**Edict** — 基于"三省六部"架构的多 Agent 协同任务执行系统

### 1.2 核心功能
用户输入任意简单或复杂任务，系统通过"三省六部"多 Agent 协作机制，自动规划、执行、验证并输出结果。

### 1.3 技术栈
| 层级 | 技术选型 |
|------|----------|
| 前端 | Vue 3 + TypeScript + Vite |
| 后端 | Python FastAPI |
| 数据库 | SQLite |
| LLM | Minimax API（支持配置切换） |
| 实时通信 | WebSocket |
| 文件存储 | 本地文件系统 |

---

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                      前端 (Vue 3)                        │
│         Kanban 视图 / Dashboard 视图（可切换）           │
└────────────────────────┬────────────────────────────────┘
                         │ WebSocket / HTTP
┌────────────────────────▼────────────────────────────────┐
│                    FastAPI 后端                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │              FSM 状态机引擎                       │   │
│  │   INIT → PLAN → REVIEW → EXECUTE → VALIDATE    │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │              三省 (控制层)                         │   │
│  │   中书省(规划) → 门下省(审核) → 尚书省(调度)       │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │              六部 (执行层)                         │   │
│  │   吏部  户部  礼部  兵部  刑部  工部               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                    SQLite + 文件系统                      │
└─────────────────────────────────────────────────────────┘
```

### 2.2 三省职责

| 部门 | 角色 | 职责 |
|------|------|------|
| **中书省** | Planner Agent | 接收用户任务，拆解为 DAG 有向无环图，输出强类型 JSON 任务列表 |
| **门下省** | Reviewer Agent | 审核任务计划的可行性、依赖关系、权限边界，不达标则驳回 |
| **尚书省** | Router Agent | 根据任务类型路由到对应六部，调度执行顺序 |

### 2.3 六部职责

| 部门 | 角色 | 职责 |
|------|------|------|
| **吏部** | Personnel | 环境配置、依赖分析、目录结构规划 |
| **户部** | Revenue | 数据状态管理、Memory 管理、Token 计数 |
| **礼部** | Rites | UI 生成、文档格式化、Markdown 输出 |
| **兵部** | War | 唯一有命令执行权限的部门（bash、网络请求） |
| **刑部** | Justice | 单元测试、异常捕获、错误追踪 |
| **工部** | Works | 核心代码生成 |

---

## 3. FSM 状态机

### 3.1 状态定义

| 状态 | 触发条件 | 执行者 | 输出 |
|------|----------|--------|------|
| `INIT` | 用户提交任务 | 系统 | 创建任务实例 |
| `PLAN` | INIT 完成 | 中书省 | DAG 任务图 |
| `REVIEW` | PLAN 完成 | 门下省 | 审核结果（通过/驳回） |
| `EXECUTE` | REVIEW 通过 | 尚书省调度六部 | 执行结果 |
| `VALIDATE` | EXECUTE 完成 | 刑部 | 验证报告 |
| `DONE` | VALIDATE 通过 | 系统 | 任务完成 |
| `FAILED` | 重试超限或异常 | 系统 | 任务失败 |
| `HUMAN_INTERVENTION` | 重试超限触发 | 系统 | 等待人工介入 |

### 3.2 状态流转图

```
 INIT ──→ PLAN ──→ REVIEW ──→ EXECUTE ──→ VALIDATE ──→ DONE
           ↓         ↓            ↓            ↓
        (驳回)    (驳回)      (驳回)      (验证失败)
           ↓         ↓            ↓            ↓
        重试      返回PLAN      重试         重试
           ↓         ↓            ↓            ↓
        ─────────────────────────────→ FAILED
                                           ↓
                                   HUMAN_INTERVENTION
```

### 3.3 防死锁机制

- 每个步骤有 `retry_count` 字段，初始值 0
- 阈值：`MAX_RETRIES = 3`
- 驳回时 `retry_count + 1`，若 ≥ 3 则流转至 `HUMAN_INTERVENTION` 或 `FAILED`
- 通过 WebSocket 实时通知前端

### 3.4 DAG 并发调度（尚书省职责）

- `task_steps.dependencies` 存储 JSON 数组，如 `["step_id_1", "step_id_2"]`
- 尚书省执行拓扑排序，仅当前置步骤状态均为 `success` 时触发当前步骤
- 使用 `asyncio.gather` 实现无依赖步骤的并发执行

### 3.5 强类型通信

所有 Agent 之间通信必须使用 Pydantic 模型，禁止自由文本：

```python
# 示例：中书省输出
class PlanOutput(BaseModel):
    task_id: str
    dag: dict  # {"nodes": [...], "edges": [...]}
    estimated_steps: int
    departments: list[str]  # 需要的部门

# 示例：六部输出
class ExecuteOutput(BaseModel):
    task_id: str
    department: str
    status: Literal["success", "failed"]
    output: dict | None
    error: str | None
```

---

## 4. 前端设计

### 4.1 视图模式

支持 **Kanban 视图** 和 **Dashboard 视图** 切换：

#### Kanban 视图
- 5 列：INIT | PLAN | REVIEW | EXECUTE | VALIDATE
- 任务卡片在各列间拖拽（只读，实际状态由后端控制）
- 点击卡片展开详情

#### Dashboard 视图
- 顶部：任务输入框 + 开始按钮
- 中部：DAG 可视化图（节点 = 子任务，边 = 依赖）
- 底部：执行日志实时滚动

### 4.2 组件结构

```
App.vue
├── Header.vue (切换视图按钮)
├── TaskInput.vue (任务输入)
├── KanbanView.vue
│   ├── KanbanColumn.vue (x5)
│   └── TaskCard.vue
├── DashboardView.vue
│   ├── DagGraph.vue (D3.js 或自定义 SVG)
│   └── ExecutionLog.vue
└── TaskDetailModal.vue (任务详情/预览/下载)
```

### 4.3 在线预览与下载

- **在线预览**：代码文件在 Modal 中高亮显示（使用 Prism.js）
- **下载压缩包**：生成 `task_{id}_output.zip`，包含所有产出文件

---

## 5. 后端设计

### 5.1 目录结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── db/
│   │   ├── database.py      # SQLite 连接
│   │   └── models.py        # SQLAlchemy 模型
│   ├── agents/              # Agent 实现
│   │   ├── base.py          # Agent 基类
│   │   ├── threeshengs/     # 三省
│   │   │   ├── zhongshu.py  # 中书省
│   │   │   ├── menxia.py    # 门下省
│   │   │   └── shangshu.py  # 尚书省
│   │   └── liubus/          # 六部
│   │       ├── li.py        # 吏部
│   │       ├── hu.py        # 户部
│   │       ├── li_rites.py  # 礼部
│   │       ├── bing.py      # 兵部
│   │       ├── xing.py      # 刑部
│   │       └── gong.py      # 工部
│   ├── fsm/
│   │   └── engine.py        # FSM 状态机引擎
│   ├── schemas/             # Pydantic 模型
│   ├── api/
│   │   ├── routes.py        # HTTP 路由
│   │   └── ws.py            # WebSocket 路由
│   └── services/
│       └── llm.py           # LLM 调用服务
├── storage/                 # 文件存储
│   └── tasks/
└── requirements.txt
```

### 5.2 API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/tasks` | 创建新任务 |
| GET | `/api/tasks` | 列出所有任务 |
| GET | `/api/tasks/{id}` | 获取任务详情 |
| GET | `/api/tasks/{id}/download` | 下载产出物压缩包 |
| WS | `/ws/tasks/{id}` | WebSocket 实时推送 |
| GET | `/api/files/{task_id}/{path}` | 在线预览文件 |

### 5.3 数据库模型

```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    user_input TEXT NOT NULL,
    status TEXT NOT NULL,  -- init|plan|review|execute|validate|done|failed
    current_state TEXT,
    dag_definition TEXT,    -- 新增：保存中书省生成的完整 DAG 结构
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE task_steps (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    step_name TEXT NOT NULL,
    department TEXT,       -- 执行的部门
    status TEXT NOT NULL,   -- pending|running|success|failed
    input_data TEXT,        -- JSON
    output_data TEXT,       -- JSON
    error TEXT,
    dependencies TEXT,      -- 新增：JSON 数组，记录依赖的 step_ids，用于尚书省并发调度
    retry_count INTEGER DEFAULT 0, -- 新增：防死循环
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE task_files (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. 上下文管理与户部职责

### 6.1 户部的核心职能：上下文裁剪

- 户部作为"数据库操作员"，只允许读写共享内存（Redis 或 JSON 文件）
- 防止其他部门私自篡改全局变量
- **上下文裁剪策略**：尚书省将任务派发给六部时，户部只提供：
  1. 全局目标简述
  2. 当前节点所需的输入变量
  3. 相关的环境依赖
  4. **绝对避免全量投喂历史对话**

## 7. JSON 容错与清理

### 7.1 输出清洗拦截器

即使使用 Pydantic 和 `response_format={"type": "json_object"}`，LLM 偶尔仍会返回带有 Markdown 标记的 JSON。

- 在 LLM 服务层增加清洗拦截器（Interceptor）
- 使用正则表达式提取纯 JSON 字符串后，再交由 Pydantic 校验

```python
import re

def extract_json(text: str) -> str:
    """从 LLM 输出中提取纯 JSON"""
    match = re.search(r'\{[\s\S]*\}', text)
    return match.group(0) if match else text
```

## 8. 安全设计

### 8.1 兵部权限控制

- 兵部是唯一允许执行 bash 命令和网络请求的部门
- 其他部门如需执行命令，必须通过尚书省调度兵部
- 命令执行有超时限制（60s）和白名单过滤

### 8.2 输入校验

- 所有用户输入使用 Pydantic 模型校验
- 禁止直接执行用户提供的原始代码
- 任务结果存储在隔离目录

---

## 9. 部署设计

### 9.1 开发模式

```bash
# 后端
cd backend && uvicorn app.main:app --reload --port 8000

# 前端
cd frontend && npm run dev
```

### 9.2 Docker 部署

```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./storage:/app/storage

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
```

---

## 10. 配置管理

```python
# backend/app/config.py
class Config:
    LLM_PROVIDER = "minimax"  # minimax | openai | claude
    MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
    MINIMAX_BASE_URL = "https://api.minimax.chat/v1"

    DATABASE_URL = "sqlite:///./storage/edict.db"
    STORAGE_PATH = "./storage/tasks"

    # Agent 超时配置
    AGENT_TIMEOUT = 120  # seconds
    COMMAND_TIMEOUT = 60  # seconds
```

---

## 11. 验收标准

1. 用户输入任务后，系统自动执行完整 FSM 流程
2. 前端实时显示任务状态（Kanban 和 Dashboard 视图可切换）
3. 六部 Agent 各自正确执行职责，输出符合 Schema
4. 任务完成后可在线预览代码和下载压缩包
5. 支持 Docker 一键部署
