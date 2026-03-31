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