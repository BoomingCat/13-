from typing import Any, Literal

from pydantic import BaseModel, Field

ChartType = Literal["table", "card", "line", "bar", "pie", "scatter"]


class ChartBuildRequest(BaseModel):
    title: str = "数据分析结果"
    columns: list[str] = Field(min_length=1)
    rows: list[list[Any]] = Field(default_factory=list)
    chart_type: ChartType | None = None
    category_column: str | None = None
    value_columns: list[str] = Field(default_factory=list)


class ChartResponse(BaseModel):
    chart_type: ChartType
    title: str
    option: dict[str, Any]
    reason: str
