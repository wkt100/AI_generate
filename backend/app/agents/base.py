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
