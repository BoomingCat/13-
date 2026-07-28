from typing import Any

from pydantic import BaseModel, Field


class ReportBuildRequest(BaseModel):
    question: str
    sql: str
    columns: list[str] = Field(default_factory=list)
    rows: list[list[Any]] = Field(default_factory=list)
    conclusion: str


class ReportBuildResponse(BaseModel):
    format: str = "markdown"
    content: str
