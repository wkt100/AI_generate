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
from app.api.ws import broadcast_task_update

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FSMEngine:
    """状态机引擎 - 管理 INIT -> PLAN -> REVIEW -> EXECUTE -> VALIDATE -> DONE 流程"""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.MAX_RETRIES = 3

    async def run(self):
        """执行完整 FSM 流程 (MVP阶段使用Mock Agent)"""
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
            await broadcast_task_update(self.task_id, "init", "INIT", {"message": "任务初始化完成"})

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
        await broadcast_task_update(self.task_id, "plan", "PLAN", {"dag_nodes": 3})

    async def _mock_menxia(self, session: AsyncSession) -> ReviewOutput:
        """Mock 门下省: 审核计划"""
        result = await session.execute(select(Task).where(Task.id == self.task_id))
        task = result.scalar_one()
        task.status = "review"
        task.current_state = "REVIEW"
        logger.info(f"[{self.task_id}] [REVIEW] 门下省审核通过")
        await broadcast_task_update(self.task_id, "review", "REVIEW", {"approved": True})
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
            await broadcast_task_update(self.task_id, "execute", "EXECUTE", {"step": step.step_name, "department": step.department})

    async def _mock_xing(self, session: AsyncSession):
        """Mock 刑部: 验证结果"""
        result = await session.execute(select(Task).where(Task.id == self.task_id))
        task = result.scalar_one()
        task.status = "validate"
        task.current_state = "VALIDATE"
        logger.info(f"[{self.task_id}] [VALIDATE] 刑部验证通过")
        await broadcast_task_update(self.task_id, "validate", "VALIDATE", {"passed": True})
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