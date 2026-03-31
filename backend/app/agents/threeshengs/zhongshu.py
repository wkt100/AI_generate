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
{{
  "nodes": [
    {{
      "id": "step_1",
      "name": "步骤名称",
      "department": "部门名称",
      "description": "步骤描述"
    }}
  ],
  "edges": [
    {{"from_node": "step_1", "to_node": "step_2"}}
  ],
  "estimated_steps": 3,
  "departments": ["工部", "刑部"]
}}

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