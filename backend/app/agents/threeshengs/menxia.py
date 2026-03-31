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
{{
  "approved": true/false,
  "reason": "审核说明",
  "suggestions": ["建议1", "建议2"]  // 如果不通过
}}

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