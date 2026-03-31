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
