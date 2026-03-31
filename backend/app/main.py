from fastapi import FastAPI, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid
from sqlalchemy import select

from app.config import Config
from app.db.database import init_db, async_session
from app.db.models import Task
from app.schemas.task import TaskCreate, TaskResponse
from app.fsm.engine import create_and_run_task
from app.api.ws import websocket_endpoint
from app.api.routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Config.ensure_dirs()
    await init_db()
    yield


app = FastAPI(title="Edict API", version="0.1.0", lifespan=lifespan)

app.include_router(api_router)

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


@app.websocket("/ws/tasks/{task_id}")
async def websocket_route(websocket: WebSocket, task_id: str):
    await websocket_endpoint(websocket, task_id)
