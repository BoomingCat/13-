from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    conversation_id: UUID | None = None


class AgentStep(BaseModel):
    name: str
    status: Literal["pending", "running", "completed", "failed"]
    detail: str


class ChartSpec(BaseModel):
    type: str
    title: str
    option: dict[str, Any]


class AnalysisResponse(BaseModel):
    task_id: UUID = Field(default_factory=uuid4)
    conversation_id: UUID = Field(default_factory=uuid4)
    question: str
    intent: str
    plan: dict[str, Any] = Field(default_factory=dict)
    sql: str | None = None
    columns: list[str] = Field(default_factory=list)
    rows: list[list[Any]] = Field(default_factory=list)
    conclusion: str
    chart: ChartSpec | None = None
    steps: list[AgentStep] = Field(default_factory=list)
