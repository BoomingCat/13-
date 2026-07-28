from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class SQLValidateRequest(BaseModel):
    sql: str = Field(min_length=1, max_length=50000)


class SQLValidateResponse(BaseModel):
    valid: bool
    normalized_sql: str | None = None
    errors: list[str] = Field(default_factory=list)


class SQLExecuteRequest(SQLValidateRequest):
    parameters: dict[str, Any] = Field(default_factory=dict)


class SQLExecutionRead(BaseModel):
    id: UUID
    sql: str
    normalized_sql: str
    status: str
    columns: list[str] = Field(default_factory=list)
    rows: list[list[Any]] = Field(default_factory=list)
    row_count: int = 0
    duration_ms: float = 0
    error: str | None = None
    created_at: datetime
