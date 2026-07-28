from pydantic import BaseModel, Field


class ColumnRead(BaseModel):
    name: str
    data_type: str
    description: str | None = None
    sample_values: list[str] = Field(default_factory=list)
    nullable: bool = True
    primary_key: bool = False
    foreign_key: str | None = None
    business_terms: list[str] = Field(default_factory=list)


class TableRead(BaseModel):
    schema_name: str
    table_name: str
    description: str | None = None
    display_name: str | None = None
    estimated_rows: int = 0
    tags: list[str] = Field(default_factory=list)
    columns: list[ColumnRead] = Field(default_factory=list)


class RelationRead(BaseModel):
    source_table: str
    source_column: str
    target_table: str
    target_column: str
    relation_type: str = "many_to_one"
    confidence: float = Field(default=1.0, ge=0, le=1)


class DataSourceRead(BaseModel):
    id: str
    name: str
    database_type: str
    host: str
    port: int
    database: str
    schemas: list[str] = Field(default_factory=list)
    enabled: bool = True
    connection_status: str = "offline"


class MetadataSearchResult(BaseModel):
    tables: list[TableRead] = Field(default_factory=list)
    columns: list[dict[str, str]] = Field(default_factory=list)
