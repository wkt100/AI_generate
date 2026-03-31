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

        # 拓扑排序 (Kahn's algorithm)
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