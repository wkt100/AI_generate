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
from app.agents.threeshengs.zhongshu import ZhongshuAgent
from app.agents.threeshengs.menxia import MenxiaAgent
from app.agents.threeshengs.shangshu import ShangshuAgent
from app.agents.liubus.gong import GongAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FSMEngine:
    """状态机引擎 - 管理 INIT -> PLAN -> REVIEW -> EXECUTE -> VALIDATE -> DONE 流程"""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.MAX_RETRIES = 3

    def log(self, task_id: str, message: str, level: str = "info"):
        """统一日志记录"""
        getattr(logger, level)(f"[{task_id}] {message}")

    async def run(self):
        """执行完整 FSM 流程"""
        async with async_session() as session:
            # INIT: 创建任务记录
            await self._init_task(session)
            await session.commit()

            # PLAN: 中书省生成 DAG
            await self._zhongshu_plan(session)
            await session.commit()

            # REVIEW: 门下省审核
            review_result = await self._menxia_review(session)
            await session.commit()

            if not review_result.get("approved", False):
                self.log(self.task_id, f"计划被驳回: {review_result.get('reason')}", "warning")
                return

            # EXECUTE: 尚书省调度六部
            await self._shangshu_execute(session)
            await session.commit()

            # VALIDATE: 刑部验证
            await self._xing_validate(session)
            await session.commit()

            # DONE
            await self._mark_done(session)
            await session.commit()

            self.log(self.task_id, "FSM 流程完成")

    async def _init_task(self, session: AsyncSession):
        """INIT 状态"""
        result = await session.execute(select(Task).where(Task.id == self.task_id))
        task = result.scalar_one_or_none()
        if task:
            task.status = "init"
            task.current_state = "INIT"
            self.log(self.task_id, "任务初始化完成")
            await broadcast_task_update(self.task_id, "init", "INIT", {"message": "任务初始化完成"})

    async def _zhongshu_plan(self, session: AsyncSession):
        """真实中书省: 生成 DAG"""
        result = await session.execute(select(Task).where(Task.id == self.task_id))
        task = result.scalar_one()
        task.status = "plan"
        task.current_state = "PLAN"
        await session.commit()

        self.log(self.task_id, "中书省开始生成 DAG")
        await broadcast_task_update(self.task_id, "plan", "PLAN", {"message": "中书省规划中"})

        agent = ZhongshuAgent()
        llm_result = await agent.execute({
            "task_id": self.task_id,
            "user_input": task.user_input
        })

        if "error" in llm_result:
            self.log(self.task_id, f"中书省执行失败: {llm_result['error']}", "error")
            return llm_result

        dag = {"nodes": llm_result.get("nodes", []), "edges": llm_result.get("edges", [])}
        task.dag_definition = json.dumps(dag)

        # 创建 TaskStep 记录
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

        await broadcast_task_update(self.task_id, "plan", "PLAN", {"dag_nodes": len(dag["nodes"])})
        self.log(self.task_id, f"中书省 DAG 生成完成: {len(dag['nodes'])} 个节点")
        return llm_result

    async def _menxia_review(self, session: AsyncSession):
        """真实门下省: 审核计划"""
        result = await session.execute(select(Task).where(Task.id == self.task_id))
        task = result.scalar_one()
        task.status = "review"
        task.current_state = "REVIEW"
        await session.commit()

        self.log(self.task_id, "门下省开始审核")
        await broadcast_task_update(self.task_id, "review", "REVIEW", {"message": "门下省审核中"})

        dag = json.loads(task.dag_definition or "{}")

        agent = MenxiaAgent()
        review_result = await agent.execute({
            "task_id": self.task_id,
            "task_description": task.user_input,
            "dag": dag
        })

        await broadcast_task_update(
            self.task_id,
            "review",
            "REVIEW",
            {"approved": review_result.get("approved", False)}
        )

        if not review_result.get("approved"):
            self.log(self.task_id, f"门下省驳回: {review_result.get('reason')}", "warning")
        else:
            self.log(self.task_id, "门下省审核通过")

        return review_result

    async def _shangshu_execute(self, session: AsyncSession):
        """真实尚书省: 调度六部执行"""
        result = await session.execute(select(Task).where(Task.id == self.task_id))
        task = result.scalar_one()
        task.status = "execute"
        task.current_state = "EXECUTE"
        await session.commit()

        self.log(self.task_id, "尚书省开始调度")
        await broadcast_task_update(self.task_id, "execute", "EXECUTE", {"message": "尚书省调度中"})

        agent = ShangshuAgent()
        schedule_result = await agent.execute({
            "task_id": self.task_id,
            "dag": json.loads(task.dag_definition or "{}")
        })

        if "error" in schedule_result:
            self.log(self.task_id, f"尚书省调度失败: {schedule_result['error']}", "error")
            return schedule_result

        # 按调度顺序执行
        for step_info in schedule_result.get("schedule", []):
            step_id = f"{self.task_id}_{step_info['id']}"
            result = await session.execute(select(TaskStep).where(TaskStep.id == step_id))
            step = result.scalar_one()
            step.status = "running"
            await session.commit()

            self.log(self.task_id, f"尚书省调度: {step_info['department']} 执行 {step_info['name']}")
            await broadcast_task_update(
                self.task_id,
                "execute",
                "EXECUTE",
                {"step": step_info['name'], "department": step_info['department']}
            )

            # 这里实际调用六部 Agent (以工部为例)
            if step_info['department'] == '工部':
                gong_agent = GongAgent()
                exec_result = await gong_agent.execute({
                    "task_id": self.task_id,
                    "task_description": task.user_input,
                    "requirements": step_info.get('description', ''),
                    "language": "python",
                    "input_spec": json.dumps(step_info)
                })

                if "error" in exec_result:
                    step.status = "failed"
                    step.error = exec_result["error"]
                    self.log(self.task_id, f"工部执行失败: {exec_result['error']}", "error")
                else:
                    step.status = "success"
                    step.output_data = json.dumps(exec_result)
                    self.log(self.task_id, f"工部执行成功")
            else:
                # 其他部门暂时用 Mock
                await asyncio.sleep(0.5)
                step.status = "success"
                step.output_data = json.dumps({"result": f"{step_info['department']} 执行完成"})
                self.log(self.task_id, f"{step_info['department']} 完成: {step_info['name']}")

            await session.commit()

        return schedule_result

    async def _xing_validate(self, session: AsyncSession):
        """刑部验证"""
        result = await session.execute(select(Task).where(Task.id == self.task_id))
        task = result.scalar_one()
        task.status = "validate"
        task.current_state = "VALIDATE"
        await session.commit()

        self.log(self.task_id, "刑部开始验证")
        await broadcast_task_update(self.task_id, "validate", "VALIDATE", {"message": "刑部验证中"})

        # 简单检查所有步骤是否成功
        steps_result = await session.execute(
            select(TaskStep).where(TaskStep.task_id == self.task_id)
        )
        steps = steps_result.scalars().all()
        all_success = all(s.status == "success" for s in steps)

        if all_success:
            self.log(self.task_id, "刑部验证通过")
            await broadcast_task_update(self.task_id, "validate", "VALIDATE", {"passed": True})
        else:
            self.log(self.task_id, "刑部验证失败: 存在未完成的步骤", "error")
            await broadcast_task_update(self.task_id, "validate", "VALIDATE", {"passed": False})

        return {"passed": all_success}

    async def _mark_done(self, session: AsyncSession):
        """标记任务完成"""
        result = await session.execute(select(Task).where(Task.id == self.task_id))
        task = result.scalar_one()
        task.status = "done"
        task.current_state = "DONE"
        task.completed_at = datetime.utcnow()
        self.log(self.task_id, "任务完成")


async def create_and_run_task(task_id: str):
    """创建任务并运行 FSM"""
    engine = FSMEngine(task_id)
    await engine.run()