import zipfile
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List

from app.config import Config
from app.db.database import async_session
from app.db.models import Task, TaskStep, TaskFile
from app.schemas.task import TaskResponse, TaskStepResponse
from sqlalchemy import select

router = APIRouter()


@router.get("/api/tasks/{task_id}/download")
async def download_task_output(task_id: str):
    """打包任务产出文件并下载"""
    storage_path = Path(Config.STORAGE_PATH) / task_id

    if not storage_path.exists():
        raise HTTPException(status_code=404, detail="Task output not found")

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


@router.get("/api/files/{task_id}/{file_path:path}")
async def preview_file(task_id: str, file_path: str):
    """在线预览文件内容"""
    full_path = Path(Config.STORAGE_PATH) / task_id / file_path

    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    content = full_path.read_text()
    return {"content": content, "filename": file_path}


@router.get("/api/tasks/{task_id}/steps", response_model=List[TaskStepResponse])
async def get_task_steps(task_id: str):
    """获取任务的所有步骤"""
    async with async_session() as session:
        result = await session.execute(
            select(TaskStep).where(TaskStep.task_id == task_id)
        )
        steps = result.scalars().all()
        return [
            TaskStepResponse(
                id=s.id,
                task_id=s.task_id,
                step_name=s.step_name,
                department=s.department,
                status=s.status,
                dependencies=s.dependencies,
                retry_count=s.retry_count
            )
            for s in steps
        ]
