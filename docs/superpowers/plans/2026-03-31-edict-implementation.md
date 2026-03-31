# Edict 多 Agent 系统 - 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建基于"三省六部"架构的多 Agent 协同执行系统，用户输入任务后自动规划、执行、验证并输出结果。

**Architecture:** MVP 优先策略——先用 Mock 数据跑通 FSM 全流程，再逐步接入真实 LLM API。前端 Vue3 实时展示状态，支持 Kanban/Dashboard 视图切换。

**Tech Stack:** Vue 3 + TypeScript + Vite (前端) | FastAPI + SQLite + asyncio (后端) | Minimax API (LLM)

---

## 项目结构总览

```
ai_edict/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   ├── agents/
│   │   │   ├── base.py
│   │   │   ├── threeshengs/
│   │   │   │   ├── zhongshu.py
│   │   │   │   ├── menxia.py
│   │   │   │   └── shangshu.py
│   │   │   └── liubus/
│   │   │       ├── li.py
│   │   │       ├── hu.py
│   │   │       ├── li_rites.py
│   │   │       ├── bing.py
│   │   │       ├── xing.py
│   │   │       └── gong.py
│   │   ├── fsm/
│   │   │   └── engine.py
│   │   ├── schemas/
│   │   ├── api/
│   │   │   ├── routes.py
│   │   │   └── ws.py
│   │   └── services/
│   │       └── llm.py
│   ├── storage/tasks/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.ts
│   │   ├── components/
│   │   ├── views/
│   │   ├── stores/
│   │   └── types/
│   ├── package.json
│   └── vite.config.ts
└── docker-compose.yml
```

---

## Phase 1: 项目脚手架

### Task 1: 后端项目初始化

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/db/__init__.py`

- [ ] **Step 1: 创建 backend/requirements.txt**

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
sqlalchemy==2.0.25
aiosqlite==0.19.0
python-multipart==0.0.6
websockets==12.0
httpx==0.26.0
python-dotenv==1.0.0
```

- [ ] **Step 2: 创建 backend/app/config.py**

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage" / "tasks"

class Config:
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "minimax")
    MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
    MINIMAX_BASE_URL = "https://api.minimax.chat/v1"

    DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/storage/edict.db"
    STORAGE_PATH = str(STORAGE_DIR)

    MAX_RETRIES = 3
    AGENT_TIMEOUT = 120
    COMMAND_TIMEOUT = 60

    @classmethod
    def ensure_dirs(cls):
        Path(cls.STORAGE_PATH).mkdir(parents=True, exist_ok=True)
        Path(cls.STORAGE_PATH).parent.parent.mkdir(parents=True, exist_ok=True)
```

- [ ] **Step 3: 创建空目录结构**

```bash
mkdir -p backend/app/db
mkdir -p backend/app/agents/threeshengs
mkdir -p backend/app/agents/liubus
mkdir -p backend/app/fsm
mkdir -p backend/app/schemas
mkdir -p backend/app/api
mkdir -p backend/app/services
mkdir -p backend/storage/tasks
touch backend/app/db/__init__.py
touch backend/app/agents/__init__.py
touch backend/app/agents/threeshengs/__init__.py
touch backend/app/agents/liubus/__init__.py
touch backend/app/fsm/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/api/__init__.py
touch backend/app/services/__init__.py
```

- [ ] **Step 4: 提交**

```bash
git add -A
git commit -m "feat: initialize backend project structure"
```

---

### Task 2: 前端项目初始化

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/vite-env.d.ts`

- [ ] **Step 1: 创建 frontend/package.json**

```json
{
  "name": "edict-frontend",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "prismjs": "^1.29.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vue-tsc": "^1.8.0"
  }
}
```

- [ ] **Step 2: 创建 frontend/vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': 'ws://localhost:8000'
    }
  }
})
```

- [ ] **Step 3: 创建 frontend/tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.vue"]
}
```

- [ ] **Step 4: 创建 frontend/index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Edict - 多Agent执行系统</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

- [ ] **Step 5: 创建 frontend/src/main.ts**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)
app.use(createPinia())
app.mount('#app')
```

- [ ] **Step 6: 创建 frontend/src/App.vue**

```vue
<template>
  <div id="app">
    <h1>Edict - 多Agent执行系统</h1>
    <router-view />
  </div>
</template>

<script setup lang="ts">
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  padding: 20px;
}
</style>
```

- [ ] **Step 7: 创建 frontend/src/vite-env.d.ts**

```typescript
/// <reference types="vite/client" />
```

- [ ] **Step 8: 提交**

```bash
git add -A
git commit -m "feat: initialize frontend Vue3 + Vite + TypeScript project"
```

---

## Phase 2: 后端核心 (MVP with Mock)

### Task 3: 数据库层

**Files:**
- Create: `backend/app/db/database.py`
- Create: `backend/app/db/models.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 backend/app/db/models.py**

```python
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    user_input = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="init")
    current_state = Column(String)
    dag_definition = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    steps = relationship("TaskStep", back_populates="task", cascade="all, delete-orphan")
    files = relationship("TaskFile", back_populates="task", cascade="all, delete-orphan")


class TaskStep(Base):
    __tablename__ = "task_steps"

    id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    step_name = Column(String, nullable=False)
    department = Column(String)  #哪个部门执行
    status = Column(String, nullable=False, default="pending")  # pending|running|success|failed
    input_data = Column(Text)  # JSON string
    output_data = Column(Text)  # JSON string
    error = Column(Text)
    dependencies = Column(Text)  # JSON array string: ["step_id_1", "step_id_2"]
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="steps")


class TaskFile(Base):
    __tablename__ = "task_files"

    id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="files")
```

- [ ] **Step 2: 创建 backend/app/db/database.py**

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.db.models import Base
from app.config import Config

engine = create_async_engine(Config.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
```

- [ ] **Step 3: 创建 backend/app/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import Config
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Config.ensure_dirs()
    await init_db()
    yield


app = FastAPI(title="Edict API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "Edict API"}
```

- [ ] **Step 4: 测试数据库连接**

```bash
cd backend
pip install -r requirements.txt
python -c "from app.db.models import Task; print('Models OK')"
```

- [ ] **Step 5: 提交**

```bash
git add -A
git commit -m "feat: add database models and connection"
```

---

### Task 4: Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/task.py`

- [ ] **Step 1: 创建 backend/app/schemas/task.py**

```python
from pydantic import BaseModel
from typing import Optional, Literal


class TaskCreate(BaseModel):
    user_input: str


class TaskResponse(BaseModel):
    id: str
    user_input: str
    status: str
    current_state: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class TaskStepResponse(BaseModel):
    id: str
    task_id: str
    step_name: str
    department: Optional[str] = None
    status: str
    dependencies: Optional[str] = None
    retry_count: int

    class Config:
        from_attributes = True


class DAGNode(BaseModel):
    id: str
    name: str
    department: str
    description: str


class DAGEdge(BaseModel):
    from_node: str
    to_node: str


class PlanOutput(BaseModel):
    task_id: str
    dag: dict  # {"nodes": [...], "edges": [...]}
    estimated_steps: int
    departments: list[str]


class ExecuteOutput(BaseModel):
    task_id: str
    department: str
    status: Literal["success", "failed"]
    output: Optional[dict] = None
    error: Optional[str] = None


class ReviewOutput(BaseModel):
    task_id: str
    approved: bool
    reason: Optional[str] = None
    suggestions: Optional[list[str]] = None


class ValidateOutput(BaseModel):
    task_id: str
    passed: bool
    test_results: Optional[dict] = None
    errors: Optional[list[str]] = None
```

- [ ] **Step 2: 提交**

```bash
git add -A
git commit -m "feat: add Pydantic schemas for task communication"
```

---

### Task 5: FSM 引擎 (Mock 版本)

**Files:**
- Create: `backend/app/fsm/engine.py`
- Modify: `backend/app/main.py`

**核心概念：** FSM 引擎是任务流转的控制器。它管理任务状态、决定下一步执行哪个 Agent、处理重试逻辑。

- [ ] **Step 1: 创建 backend/app/fsm/engine.py**

```python
import asyncio
import json
import uuid
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Task, TaskStep
from app.db.database import async_session
from app.schemas.task import PlanOutput, ReviewOutput, ExecuteOutput, ValidateOutput

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FSMEngine:
    """状态机引擎 - 管理 INIT -> PLAN -> REVIEW -> EXECUTE -> VALIDATE -> DONE 流程"""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.MAX_RETRIES = 3

    async def run(self):
        """执行完整 FSM 流程 (MVP阶段使用 Mock Agent)"""
        async with async_session() as session:
            # INIT: 创建任务记录
            await self._init_task(session)
            await session.commit()

            # PLAN: 中书省生成 DAG (Mock)
            await self._mock_zhongshu(session)
            await session.commit()

            # REVIEW: 门下省审核 (Mock)
            review_result = await self._mock_menxia(session)
            await session.commit()

            if not review_result.approved:
                logger.info(f"[{self.task_id}] 计划被驳回: {review_result.reason}")
                return

            # EXECUTE: 尚书省调度六部 (Mock)
            await self._mock_shangshu(session)
            await session.commit()

            # VALIDATE: 刑部验证 (Mock)
            await self._mock_xing(session)
            await session.commit()

            # DONE
            await self._mark_done(session)
            await session.commit()

            logger.info(f"[{self.task_id}] FSM 流程完成")

    async def _init_task(self, session: AsyncSession):
        """INIT 状态"""
        result = await session.execute(select(Task).where(Task.id == self.task_id))
        task = result.scalar_one_or_none()
        if task:
            task.status = "init"
            task.current_state = "INIT"
            logger.info(f"[{self.task_id}] [INIT] 任务初始化完成")

    async def _mock_zhongshu(self, session: AsyncSession):
        """Mock 中书省: 生成 DAG"""
        result = await session.execute(select(Task).where(Task.id == self.task_id))
        task = result.scalar_one()

        # 模拟 DAG 输出
        dag = {
            "nodes": [
                {"id": "step_1", "name": "环境配置", "department": "吏部", "description": "初始化项目环境"},
                {"id": "step_2", "name": "代码生成", "department": "工部", "description": "生成核心代码"},
                {"id": "step_3", "name": "测试验证", "department": "刑部", "description": "执行单元测试"},
            ],
            "edges": [
                {"from_node": "step_1", "to_node": "step_2"},
                {"from_node": "step_2", "to_node": "step_3"},
            ]
        }

        # 更新任务状态
        task.status = "plan"
        task.current_state = "PLAN"
        task.dag_definition = json.dumps(dag)

        # 创建步骤记录
        for node in dag["nodes"]:
            step = TaskStep(
                id=f"{self.task_id}_{node['id']}",
                task_id=self.task_id,
                step_name=node["name"],
                department=node["department"],
                status="pending",
                dependencies="[]"
            )
            session.add(step)

        # 设置依赖关系
        for edge in dag["edges"]:
            from_step_id = f"{self.task_id}_{edge['from_node']}"
            to_step_id = f"{self.task_id}_{edge['to_node']}"
            result = await session.execute(select(TaskStep).where(TaskStep.id == to_step_id))
            to_step = result.scalar_one()
            deps = json.loads(to_step.dependencies)
            deps.append(from_step_id)
            to_step.dependencies = json.dumps(deps)

        logger.info(f"[{self.task_id}] [PLAN] 中书省生成 DAG: 3 个步骤")

    async def _mock_menxia(self, session: AsyncSession) -> ReviewOutput:
        """Mock 门下省: 审核计划"""
        result = await session.execute(select(Task).where(Task.id == self.task_id))
        task = result.scalar_one()
        task.status = "review"
        task.current_state = "REVIEW"
        logger.info(f"[{self.task_id}] [REVIEW] 门下省审核通过")
        return ReviewOutput(task_id=self.task_id, approved=True, reason="计划合理")

    async def _mock_shangshu(self, session: AsyncSession):
        """Mock 尚书省: 调度六部执行"""
        result = await session.execute(select(Task).where(Task.id == self.task_id))
        task = result.scalar_one()
        task.status = "execute"
        task.current_state = "EXECUTE"

        # 按拓扑序执行步骤 (MVP: 串行)
        steps_result = await session.execute(
            select(TaskStep)
            .where(TaskStep.task_id == self.task_id)
            .order_by(TaskStep.created_at)
        )
        steps = steps_result.scalars().all()

        for step in steps:
            step.status = "running"
            await session.commit()

            # 模拟执行 (Mock)
            await asyncio.sleep(0.5)  # 模拟耗时

            step.status = "success"
            step.output_data = json.dumps({"result": f"{step.department} 执行完成"})
            await session.commit()
            logger.info(f"[{self.task_id}] [EXECUTE] {step.department} 完成: {step.step_name}")

    async def _mock_xing(self, session: AsyncSession):
        """Mock 刑部: 验证结果"""
        result = await session.execute(select(Task).where(Task.id == self.task_id))
        task = result.scalar_one()
        task.status = "validate"
        task.current_state = "VALIDATE"
        logger.info(f"[{self.task_id}] [VALIDATE] 刑部验证通过")
        return ValidateOutput(task_id=self.task_id, passed=True)

    async def _mark_done(self, session: AsyncSession):
        """标记任务完成"""
        result = await session.execute(select(Task).where(Task.id == self.task_id))
        task = result.scalar_one()
        task.status = "done"
        task.current_state = "DONE"
        task.completed_at = datetime.utcnow()
        logger.info(f"[{self.task_id}] [DONE] 任务完成")


async def create_and_run_task(task_id: str):
    """创建任务并运行 FSM"""
    engine = FSMEngine(task_id)
    await engine.run()
```

- [ ] **Step 2: 更新 backend/app/main.py**

```python
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid

from app.config import Config
from app.db.database import init_db, async_session
from app.db.models import Task
from app.fsm.engine import create_and_run_task
from app.schemas.task import TaskCreate, TaskResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    Config.ensure_dirs()
    await init_db()
    yield


app = FastAPI(title="Edict API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(task_data: TaskCreate, background_tasks: BackgroundTasks):
    """创建新任务并启动 FSM"""
    task_id = str(uuid.uuid4())[:8]

    async with async_session() as session:
        task = Task(
            id=task_id,
            user_input=task_data.user_input,
            status="creating",
            current_state="INIT"
        )
        session.add(task)
        await session.commit()

    # 后台运行 FSM
    background_tasks.add_task(create_and_run_task, task_id)

    return TaskResponse(
        id=task_id,
        user_input=task_data.user_input,
        status="creating",
        current_state="INIT"
    )


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            return {"error": "Task not found"}
        return TaskResponse(
            id=task.id,
            user_input=task.user_input,
            status=task.status,
            current_state=task.current_state
        )


@app.get("/api/tasks")
async def list_tasks():
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(Task))
        tasks = result.scalars().all()
        return [
            TaskResponse(
                id=t.id,
                user_input=t.user_input,
                status=t.status,
                current_state=t.current_state
            )
            for t in tasks
        ]
```

- [ ] **Step 3: 测试 FSM 引擎**

```bash
cd backend
python -c "
import asyncio
from app.db.database import init_db, async_session
from app.db.models import Task
from app.fsm.engine import create_and_run_task
import uuid

async def test():
    await init_db()
    task_id = 'test_001'
    async with async_session() as session:
        task = Task(id=task_id, user_input='写一个计算器', status='creating', current_state='INIT')
        session.add(task)
        await session.commit()
    await create_and_run_task(task_id)
    print('FSM test completed')

asyncio.run(test())
"
```

Expected output: `FSM test completed` with logs showing INIT → PLAN → REVIEW → EXECUTE → VALIDATE → DONE

- [ ] **Step 4: 提交**

```bash
git add -A
git commit -m "feat: add FSM engine with mock agents for MVP"
```

---

### Task 6: WebSocket 实时推送

**Files:**
- Create: `backend/app/api/ws.py`
- Modify: `backend/app/main.py`

**核心概念：** WebSocket 让后端能主动推送状态变化给前端。FSM 每完成一个步骤，就通过 WebSocket 通知前端更新 UI。

- [ ] **Step 1: 创建 backend/app/api/ws.py**

```python
import asyncio
import json
import logging
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, task_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[task_id] = websocket
        logger.info(f"[WS] Client connected for task {task_id}")

    def disconnect(self, task_id: str):
        if task_id in self.active_connections:
            del self.active_connections[task_id]
            logger.info(f"[WS] Client disconnected for task {task_id}")

    async def send_message(self, task_id: str, message: dict):
        if task_id in self.active_connections:
            await self.active_connections[task_id].send_json(message)
            logger.info(f"[WS] Sent message to {task_id}: {message}")


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket 端点: ws://host/ws/tasks/{task_id}"""
    await manager.connect(task_id, websocket)
    try:
        while True:
            # 保持连接，等待后端推送消息
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(task_id)


async def broadcast_task_update(task_id: str, status: str, current_state: str, step_info: dict = None):
    """FSM 引擎调用此方法推送状态更新"""
    message = {
        "type": "task_update",
        "task_id": task_id,
        "status": status,
        "current_state": current_state,
    }
    if step_info:
        message["step"] = step_info

    await manager.send_message(task_id, message)
```

- [ ] **Step 2: 更新 backend/app/main.py**

```python
from fastapi import FastAPI, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid

from app.config import Config
from app.db.database import init_db, async_session
from app.db.models import Task
from app.fsm.engine import create_and_run_task
from app.schemas.task import TaskCreate, TaskResponse
from app.api.ws import websocket_endpoint, broadcast_task_update


@asynccontextmanager
async def lifespan(app: FastAPI):
    Config.ensure_dirs()
    await init_db()
    yield


app = FastAPI(title="Edict API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ... 保留之前的 @app.post 和 @app.get 端点 ...
# (同上，无需修改)

@app.websocket("/ws/tasks/{task_id}")
async def websocket_route(websocket: WebSocket, task_id: str):
    await websocket_endpoint(websocket, task_id)
```

- [ ] **Step 3: 更新 FSM 引擎添加 WebSocket 推送**

在 `backend/app/fsm/engine.py` 中修改各方法添加 WebSocket 推送:

```python
async def _init_task(self, session: AsyncSession):
    # ... existing code ...
    await broadcast_task_update(self.task_id, "init", "INIT", {"message": "任务初始化完成"})

async def _mock_zhongshu(self, session: AsyncSession):
    # ... existing code ...
    await broadcast_task_update(self.task_id, "plan", "PLAN", {"dag_nodes": 3})

async def _mock_menxia(self, session: AsyncSession) -> ReviewOutput:
    # ... existing code ...
    await broadcast_task_update(self.task_id, "review", "REVIEW", {"approved": True})

async def _mock_shangshu(self, session: AsyncSession):
    # ... existing code ...
    await broadcast_task_update(self.task_id, "execute", "EXECUTE", {"step": step.step_name})

async def _mock_xing(self, session: AsyncSession):
    # ... existing code ...
    await broadcast_task_update(self.task_id, "validate", "VALIDATE", {"passed": True})
```

- [ ] **Step 4: 提交**

```bash
git add -A
git commit -m "feat: add WebSocket for real-time task updates"
```

---

## Phase 3: 前端 MVP

### Task 7: 前端核心组件 (Kanban 视图)

**Files:**
- Create: `frontend/src/components/KanbanColumn.vue`
- Create: `frontend/src/components/TaskCard.vue`
- Create: `frontend/src/components/TaskInput.vue`
- Create: `frontend/src/views/KanbanView.vue`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: 创建 frontend/src/components/KanbanColumn.vue**

```vue
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
```

- [ ] **Step 2: 创建 frontend/src/components/TaskCard.vue**

```vue
<template>
  <div class="task-card" @click="$emit('click')">
    <div class="task-id">#{{ task.id }}</div>
    <div class="task-input">{{ truncatedInput }}</div>
    <div class="task-state" :class="stateClass">{{ task.current_state }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  task: {
    id: string
    user_input: string
    status: string
    current_state: string
  }
}>()

defineEmits<{
  (e: 'click'): void
}>()

const truncatedInput = computed(() => {
  const input = props.task.user_input
  return input.length > 50 ? input.substring(0, 50) + '...' : input
})

const stateClass = computed(() => {
  const state = props.task.status
  return {
    'state-init': state === 'init' || state === 'creating',
    'state-active': ['plan', 'review', 'execute', 'validate'].includes(state),
    'state-done': state === 'done',
    'state-failed': state === 'failed' || state === 'human_intervention'
  }
})
</script>

<style scoped>
.task-card {
  background: white;
  border-radius: 6px;
  padding: 12px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  transition: box-shadow 0.2s;
}
.task-card:hover {
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.task-id {
  font-size: 11px;
  color: #94a3b8;
  font-family: monospace;
}
.task-input {
  font-size: 13px;
  color: #1e293b;
  margin: 8px 0;
  line-height: 1.4;
}
.task-state {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
  display: inline-block;
}
.state-init { background: #fef3c7; color: #92400e; }
.state-active { background: #dbeafe; color: #1e40af; }
.state-done { background: #d1fae5; color: #065f46; }
.state-failed { background: #fee2e2; color: #991b1b; }
</style>
```

- [ ] **Step 3: 创建 frontend/src/components/TaskInput.vue**

```vue
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
  // loading 状态将在父组件中管理
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
```

- [ ] **Step 4: 创建 frontend/src/views/KanbanView.vue**

```vue
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
import { ref, computed, onMounted } from 'vue'
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
  const res = await fetch('/api/tasks')
  tasks.value = await res.json()
}

const onSubmitTask = async (description: string) => {
  const res = await fetch('/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_input: description })
  })
  const task = await res.json()
  tasks.value.push(task)
}

const onSelectTask = (task: any) => {
  console.log('Selected task:', task)
  // TODO: 打开详情 Modal
}

const connectWebSocket = (taskId: string) => {
  ws.value = new WebSocket(`ws://localhost:8000/ws/tasks/${taskId}`)
  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data)
    const task = tasks.value.find(t => t.id === data.task_id)
    if (task) {
      task.status = data.status
      task.current_state = data.current_state
    }
  }
}

onMounted(() => {
  fetchTasks()
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
```

- [ ] **Step 5: 更新 frontend/src/App.vue**

```vue
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
```

- [ ] **Step 6: 创建 DashboardView 占位符**

```vue
<template>
  <div class="dashboard-view">
    <div class="coming-soon">
      <h2>仪表盘视图</h2>
      <p>DAG 可视化和执行日志将显示在这里</p>
    </div>
  </div>
</template>

<style scoped>
.dashboard-view {
  padding: 20px;
}
.coming-soon {
  text-align: center;
  padding: 60px;
  color: #64748b;
}
</style>
```

- [ ] **Step 7: 提交**

```bash
git add -A
git commit -m "feat: add Kanban view and basic frontend components"
```

---

## Phase 4: 真实 Agent 集成

### Task 8: LLM 服务层 (含 JSON 清洗)

**Files:**
- Create: `backend/app/services/llm.py`
- Modify: `backend/app/config.py`

- [ ] **Step 1: 创建 backend/app/services/llm.py**

```python
import re
import json
import httpx
import logging
from typing import Optional
from app.config import Config

logger = logging.getLogger(__name__)


def extract_json(text: str) -> str:
    """
    从 LLM 输出中提取纯 JSON。
    处理常见的 Markdown 包裹情况: ```json ... ``` 或 ``` ... ```
    """
    # 移除 Markdown code blocks
    patterns = [
        r'```json\s*([\s\S]*?)\s*```',
        r'```\s*([\s\S]*?)\s*```',
        r'(\{[\s\S]*\})',  # 直接找第一个 {...}
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            potential = match.group(1) if '```' in pattern else match.group(0)
            try:
                json.loads(potential.strip())
                return potential.strip()
            except json.JSONDecodeError:
                continue

    # 最后尝试直接解析原文本
    return text.strip()


async def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    response_format: Optional[dict] = None
) -> str:
    """
    调用 LLM API (Minimax)。
    返回纯文本响应。
    """
    if Config.LLM_PROVIDER == "minimax":
        return await _call_minimax(prompt, system_prompt, response_format)
    else:
        raise ValueError(f"Unsupported LLM provider: {Config.LLM_PROVIDER}")


async def _call_minimax(
    prompt: str,
    system_prompt: Optional[str] = None,
    response_format: Optional[dict] = None
) -> str:
    """调用 Minimax API"""
    url = f"{Config.MINIMAX_BASE_URL}/text/chatcompletion_v2"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "abab6.5s-chat",
        "messages": messages,
    }

    if response_format:
        payload["response_format"] = response_format

    headers = {
        "Authorization": f"Bearer {Config.MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=Config.AGENT_TIMEOUT) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def call_llm_json(prompt: str, system_prompt: Optional[str] = None) -> dict:
    """
    调用 LLM 并强制返回 JSON。
    自动处理 Markdown 包裹和解析错误。
    """
    raw_text = await call_llm(
        prompt,
        system_prompt,
        response_format={"type": "json_object"}
    )

    clean_text = extract_json(raw_text)

    try:
        return json.loads(clean_text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}\nRaw: {raw_text}\nClean: {clean_text}")
        raise ValueError(f"Failed to parse LLM response as JSON: {clean_text[:200]}")
```

- [ ] **Step 2: 提交**

```bash
git add -A
git commit -m "feat: add LLM service with JSON cleaning interceptor"
```

---

### Task 9: Agent 基类

**Files:**
- Create: `backend/app/agents/base.py`

- [ ] **Step 1: 创建 backend/app/agents/base.py**

```python
from abc import ABC, abstractmethod
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class Agent(ABC):
    """
    Agent 基类。
    所有三省六部都继承此类。
    """

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    @abstractmethod
    async def execute(self, input_data: dict) -> dict:
        """
        执行 Agent 逻辑。
        输入输出都必须符合 Pydantic Schema。
        """
        pass

    def log(self, task_id: str, message: str, level: str = "info"):
        """带结构的日志"""
        getattr(logger, level)(f"[{task_id}] [{self.name}] {message}")

    async def validate_input(self, input_data: dict, expected_keys: list[str]) -> bool:
        """简单的输入校验"""
        for key in expected_keys:
            if key not in input_data:
                self.log("UNKNOWN", f"Missing required key: {key}", "error")
                return False
        return True
```

- [ ] **Step 2: 提交**

```bash
git add -A
git commit -m "feat: add Agent base class"
```

---

### Task 10: 三省 Agent 实现

**Files:**
- Create: `backend/app/agents/threeshengs/zhongshu.py`
- Create: `backend/app/agents/threeshengs/menxia.py`
- Create: `backend/app/agents/threeshengs/shangshu.py`

- [ ] **Step 1: 创建 backend/app/agents/threeshengs/zhongshu.py**

```python
from app.agents.base import Agent
from app.services.llm import call_llm_json


PROMPT_ZHONGSHU = """你是一个任务规划专家（中书省）。

## 你的职责
1. 接收用户的任务描述
2. 将任务拆解为 DAG（有向无环图）形式的子任务
3. 每个子任务必须分配给正确的部门

## 部门职责参考
- 吏部: 环境配置、依赖管理
- 户部: 数据状态、内存管理
- 礼部: UI生成、文档格式化
- 兵部: 命令执行、API调用
- 刑部: 测试验证、异常处理
- 工部: 核心代码生成

## 输出格式 (JSON)
{
  "nodes": [
    {
      "id": "step_1",
      "name": "步骤名称",
      "department": "部门名称",
      "description": "步骤描述"
    }
  ],
  "edges": [
    {"from_node": "step_1", "to_node": "step_2"}
  ],
  "estimated_steps": 3,
  "departments": ["工部", "刑部"]
}

## 注意事项
- 绝对不要生成循环依赖
- 步骤数量控制在 3-10 个
- 必须有明确的执行顺序

用户任务: {user_input}
"""


class ZhongshuAgent(Agent):
    """中书省 - 任务规划 Agent"""

    def __init__(self):
        super().__init__("中书省", "Planner")

    async def execute(self, input_data: dict) -> dict:
        user_input = input_data.get("user_input", "")

        if not await self.validate_input(input_data, ["user_input"]):
            return {"error": "Missing user_input"}

        self.log(input_data.get("task_id", "UNKNOWN"), "开始生成 DAG")

        try:
            result = await call_llm_json(
                PROMPT_ZHONGSHU.format(user_input=user_input),
                system_prompt="你是一个专业的任务规划专家。必须返回合法的 JSON 格式。"
            )
            result["task_id"] = input_data.get("task_id")
            self.log(input_data.get("task_id", "UNKNOWN"), f"DAG 生成完成: {len(result.get('nodes', []))} 个节点")
            return result
        except Exception as e:
            self.log(input_data.get("task_id", "UNKNOWN"), f"DAG 生成失败: {e}", "error")
            return {"error": str(e)}
```

- [ ] **Step 2: 创建 backend/app/agents/threeshengs/menxia.py**

```python
from app.agents.base import Agent
from app.services.llm import call_llm_json


PROMPT_MENXIA = """你是一个严格的质量审核专家（门下省）。

## 你的职责
1. 审核中书省生成的 DAG 计划
2. 检查依赖关系是否合理（无循环依赖）
3. 检查部门分配是否正确
4. 检查步骤是否完整覆盖任务需求

## 审核标准
- DAG 必须是无环图
- 每个步骤必须有明确的执行部门
- 步骤之间必须有合理的依赖关系
- 不能遗漏关键步骤

## 输出格式 (JSON)
{
  "approved": true/false,
  "reason": "审核说明",
  "suggestions": ["建议1", "建议2"]  // 如果不通过
}

任务: {task_description}
DAG计划: {dag_json}
"""


class MenxiaAgent(Agent):
    """门下省 - 质量审核 Agent"""

    def __init__(self):
        super().__init__("门下省", "Reviewer")

    async def execute(self, input_data: dict) -> dict:
        task_description = input_data.get("task_description", "")
        dag = input_data.get("dag", {})

        if not await self.validate_input(input_data, ["task_description", "dag"]):
            return {"approved": False, "reason": "Invalid input"}

        self.log(input_data.get("task_id", "UNKNOWN"), "开始审核 DAG")

        try:
            result = await call_llm_json(
                PROMPT_MENXIA.format(
                    task_description=task_description,
                    dag_json=str(dag)
                ),
                system_prompt="你是一个严格的质量审核专家。必须返回合法的 JSON 格式。"
            )
            self.log(
                input_data.get("task_id", "UNKNOWN"),
                f"审核完成: {'通过' if result.get('approved') else '驳回'}"
            )
            return result
        except Exception as e:
            self.log(input_data.get("task_id", "UNKNOWN"), f"审核失败: {e}", "error")
            return {"approved": False, "reason": str(e)}
```

- [ ] **Step 3: 创建 backend/app/agents/threeshengs/shangshu.py**

```python
from app.agents.base import Agent
from typing import Literal


class ShangshuAgent(Agent):
    """尚书省 - 路由调度 Agent"""

    def __init__(self):
        super().__init__("尚书省", "Router")

    async def execute(self, input_data: dict) -> dict:
        """
        尚书省负责调度六部执行任务。
        MVP 版本: 简单的拓扑排序 + 串行执行。
        进阶版本: asyncio.gather 并发执行无依赖的步骤。
        """
        dag = input_data.get("dag", {})
        task_id = input_data.get("task_id", "UNKNOWN")

        self.log(task_id, "开始 DAG 调度")

        nodes = dag.get("nodes", [])
        edges = dag.get("edges", [])

        # 构建依赖图
        in_degree = {node["id"]: 0 for node in nodes}
        adj_list = {node["id"]: [] for node in nodes}

        for edge in edges:
            in_degree[edge["to_node"]] = in_degree.get(edge["to_node"], 0) + 1
            adj_list[edge["from_node"]].append(edge["to_node"])

        # 拓扑排序 ( Kahn's algorithm )
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        execution_order = []

        while queue:
            current = queue.pop(0)
            execution_order.append(current)
            for neighbor in adj_list[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(execution_order) != len(nodes):
            return {"error": "DAG 存在循环依赖"}

        self.log(task_id, f"调度顺序: {' -> '.join(execution_order)}")

        return {
            "task_id": task_id,
            "execution_order": execution_order,
            "schedule": [
                next(n for n in nodes if n["id"] == step_id)
                for step_id in execution_order
            ]
        }
```

- [ ] **Step 4: 提交**

```bash
git add -A
git commit -m "feat: implement Three Departments (三省) agents"
```

---

### Task 11: 六部 Agent 实现 (以工部为例)

**Files:**
- Create: `backend/app/agents/liubus/gong.py` (工部 - 核心代码生成)

- [ ] **Step 1: 创建 backend/app/agents/liubus/gong.py**

```python
from app.agents.base import Agent
from app.services.llm import call_llm_json


PROMPT_GONG = """你是一个专业的程序员（工部）。

## 你的职责
根据指定的输入规格，生成高质量的代码。

## 约束
1. 只输出纯代码，不要任何 Markdown 标记
2. 不要写任何解释、注释或道歉
3. 使用精确的类名/函数名
4. 代码必须可以运行

## 输入规格
任务: {task_description}
语言: {language}
要求: {requirements}

## 输出格式 (JSON)
{
  "file_path": "src/example.py",
  "content": "这里放完整的代码内容，使用 \\n 表示换行"
}

任务输入规格:
{input_spec}
"""


class GongAgent(Agent):
    """工部 - 核心代码生成 Agent"""

    def __init__(self):
        super().__init__("工部", "CodeGenerator")

    async def execute(self, input_data: dict) -> dict:
        task_description = input_data.get("task_description", "")
        requirements = input_data.get("requirements", "")
        language = input_data.get("language", "python")
        input_spec = input_data.get("input_spec", "")

        self.log(input_data.get("task_id", "UNKNOWN"), f"开始生成 {language} 代码")

        try:
            result = await call_llm_json(
                PROMPT_GONG.format(
                    task_description=task_description,
                    requirements=requirements,
                    language=language,
                    input_spec=input_spec
                ),
                system_prompt="你是一个专业的程序员。必须返回合法的 JSON 格式。"
            )
            self.log(input_data.get("task_id", "UNKNOWN"), "代码生成完成")
            return result
        except Exception as e:
            self.log(input_data.get("task_id", "UNKNOWN"), f"代码生成失败: {e}", "error")
            return {"error": str(e)}
```

**注：其他五部（吏部、户部、礼部、兵部、刑部）结构类似，逐步实现。**

- [ ] **Step 2: 提交**

```bash
git add -A
git commit -m "feat: implement Ministry of Works (工部) agent"
```

---

### Task 12: 更新 FSM 引擎接入真实 Agent

**Files:**
- Modify: `backend/app/fsm/engine.py`

- [ ] **Step 1: 更新 FSM 引擎**

```python
# 替换 mock 方法为真实调用

from app.agents.threeshengs.zhongshu import ZhongshuAgent
from app.agents.threeshengs.menxia import MenxiaAgent
from app.agents.threeshengs.shangshu import ShangshuAgent
from app.agents.liubus.gong import GongAgent

async def _zhongshu_plan(self, session: AsyncSession):
    """真实中书省: 生成 DAG"""
    # ... 保留 INIT 状态更新代码 ...

    agent = ZhongshuAgent()
    result = await agent.execute({
        "task_id": self.task_id,
        "user_input": task.user_input
    })

    if "error" in result:
        raise Exception(f"中书省执行失败: {result['error']}")

    task.dag_definition = json.dumps({"nodes": result["nodes"], "edges": result["edges"]})
    # ... 创建 TaskStep 记录代码类似 ...
```

- [ ] **Step 2: 提交**

```bash
git add -A
git commit -m "feat: integrate real agents into FSM engine"
```

---

## Phase 5: 完善与部署

### Task 13: 在线预览与下载功能

**Files:**
- Create: `backend/app/api/routes.py` (增强)
- Modify: `frontend/src/components/TaskDetailModal.vue`

- [ ] **Step 1: 增强 backend/app/api/routes.py**

```python
import zipfile
from fastapi.responses import FileResponse
from pathlib import Path


@app.get("/api/tasks/{task_id}/download")
async def download_task_output(task_id: str):
    """打包任务产出文件并下载"""
    storage_path = Path(Config.STORAGE_PATH) / task_id

    if not storage_path.exists():
        return {"error": "Task output not found"}

    # 创建临时 zip
    zip_path = Path(f"/tmp/{task_id}_output.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in storage_path.rglob("*"):
            if file_path.is_file():
                zf.write(file_path, file_path.relative_to(storage_path))

    return FileResponse(
        zip_path,
        filename=f"task_{task_id}_output.zip",
        media_type="application/zip"
    )


@app.get("/api/files/{task_id}/{file_path:path}")
async def preview_file(task_id: str, file_path: str):
    """在线预览文件内容"""
    full_path = Path(Config.STORAGE_PATH) / task_id / file_path

    if not full_path.exists():
        return {"error": "File not found"}

    content = full_path.read_text()
    return {"content": content, "filename": file_path}
```

- [ ] **Step 2: 提交**

```bash
git add -A
git commit -m "feat: add file download and preview endpoints"
```

---

### Task 14: Docker 部署

**Files:**
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`
- Create: `docker-compose.yml`

- [ ] **Step 1: 创建 backend/Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

RUN mkdir -p /app/storage/tasks

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: 创建 frontend/Dockerfile**

```dockerfile
FROM node:20-alpine as builder

WORKDIR /app
COPY frontend/package*.json .
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

- [ ] **Step 3: 创建 frontend/nginx.conf**

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
    }

    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

- [ ] **Step 4: 创建 docker-compose.yml**

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./storage:/app/storage
    environment:
      - LLM_PROVIDER=minimax
      - MINIMAX_API_KEY=${MINIMAX_API_KEY}

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  storage:
```

- [ ] **Step 5: 提交**

```bash
git add -A
git commit -m "feat: add Docker deployment configuration"
```

---

## 实施检查清单

| 阶段 | 任务 | 状态 |
|------|------|------|
| Phase 1 | 1. 后端脚手架 | ☐ |
| Phase 1 | 2. 前端脚手架 | ☐ |
| Phase 2 | 3. 数据库层 | ☐ |
| Phase 2 | 4. Pydantic Schemas | ☐ |
| Phase 2 | 5. FSM 引擎 (Mock) | ☐ |
| Phase 2 | 6. WebSocket | ☐ |
| Phase 3 | 7. 前端 Kanban | ☐ |
| Phase 4 | 8. LLM 服务层 | ☐ |
| Phase 4 | 9. Agent 基类 | ☐ |
| Phase 4 | 10. 三省 Agent | ☐ |
| Phase 4 | 11. 六部 Agent | ☐ |
| Phase 4 | 12. FSM 集成真实 Agent | ☐ |
| Phase 5 | 13. 预览/下载 | ☐ |
| Phase 5 | 14. Docker | ☐ |

---

## 后续迭代建议

1. **Phase 1-3 完成后**: MVP 可运行，验证 FSM 流转和 WebSocket
2. **Phase 4 完成后**: 真实 LLM 接入，可处理实际任务
3. **Phase 5 完成后**: 完整系统，支持 Docker 部署
4. **持续优化**:
   - 添加更多六部 Agent 实现
   - 优化 DAG 拓扑排序为真正并发
   - 添加户部的上下文裁剪逻辑
   - 添加更详细的日志和错误处理
