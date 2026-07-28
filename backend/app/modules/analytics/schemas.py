from typing import Any, Literal

from pydantic import BaseModel, Field


class DatasetPayload(BaseModel):
    columns: list[str] = Field(min_length=1)
    rows: list[list[Any]] = Field(default_factory=list)


class SummaryRequest(DatasetPayload):
    numeric_columns: list[str] = Field(default_factory=list)


class ColumnSummary(BaseModel):
    column: str
    count: int
    missing: int
    minimum: float | None = None
    maximum: float | None = None
    mean: float | None = None
    total: float | None = None


class SummaryResponse(BaseModel):
    row_count: int
    summaries: list[ColumnSummary]


class RankingRequest(DatasetPayload):
    category_column: str
    value_column: str
    order: Literal["asc", "desc"] = "desc"
    limit: int = Field(default=10, ge=1, le=100)


class AnomalyRequest(DatasetPayload):
    value_column: str
    threshold: float = Field(default=2.0, gt=0)


class AnalysisRowsResponse(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
