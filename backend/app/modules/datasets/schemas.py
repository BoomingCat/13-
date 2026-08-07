from typing import Any

from pydantic import BaseModel, Field


class DatasetColumn(BaseModel):
    name: str
    data_type: str
    nullable: bool = False
    sample_values: list[Any] = Field(default_factory=list)


class DatasetSummary(BaseModel):
    name: str
    filename: str
    row_count: int
    column_count: int
    columns: list[str] = Field(default_factory=list)


class DatasetDetail(DatasetSummary):
    path: str
    column_schema: list[DatasetColumn] = Field(default_factory=list)


class DatasetRows(BaseModel):
    dataset: str
    columns: list[str]
    rows: list[dict[str, Any]]
    offset: int
    limit: int
    returned: int
    total: int


class DatasetStatus(BaseModel):
    configured: bool
    available: bool
    directory: str
    csv_count: int
