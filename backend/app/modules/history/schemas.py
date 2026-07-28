from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AnalysisHistoryRead(BaseModel):
    task_id: UUID
    conversation_id: UUID
    question: str
    intent: str
    plan: dict[str, Any] = Field(default_factory=dict)
    sql: str | None = None
    columns: list[str] = Field(default_factory=list)
    rows: list[list[Any]] = Field(default_factory=list)
    conclusion: str
    chart: dict[str, Any] | None = None
    steps: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
