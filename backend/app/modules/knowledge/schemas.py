from datetime import datetime

from pydantic import BaseModel, Field


class ObjectBase(BaseModel):
    object_code: str = Field(pattern=r"^[a-z][a-z0-9_]*$", max_length=100)
    object_name: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=50)
    description: str = ""
    source_table: str | None = None
    status: str = "active"


class ObjectCreate(ObjectBase):
    pass


class ObjectUpdate(BaseModel):
    object_name: str | None = None
    category: str | None = None
    description: str | None = None
    source_table: str | None = None
    status: str | None = None


class ObjectRead(ObjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class MetricBase(BaseModel):
    metric_code: str = Field(pattern=r"^[a-z][a-z0-9_]*$", max_length=100)
    metric_name: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=50)
    description: str = ""
    formula_expression: str = Field(min_length=1)
    unit: str | None = None
    time_field: str | None = None
    source_tables: list[str] = Field(default_factory=list)
    dimension_fields: list[str] = Field(default_factory=list)
    synonyms: list[str] = Field(default_factory=list)
    status: str = "active"


class MetricCreate(MetricBase):
    pass


class MetricUpdate(BaseModel):
    metric_name: str | None = None
    category: str | None = None
    description: str | None = None
    formula_expression: str | None = None
    unit: str | None = None
    time_field: str | None = None
    source_tables: list[str] | None = None
    dimension_fields: list[str] | None = None
    synonyms: list[str] | None = None
    status: str | None = None


class MetricRead(MetricBase):
    id: int
    version: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class RuleBase(BaseModel):
    rule_code: str = Field(pattern=r"^[a-z][a-z0-9_]*$", max_length=100)
    rule_name: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=50)
    rule_type: str = Field(min_length=1, max_length=50)
    expression: str = Field(min_length=1)
    description: str = ""
    priority: int = Field(default=100, ge=0)
    status: str = "active"


class RuleCreate(RuleBase):
    pass


class RuleUpdate(BaseModel):
    rule_name: str | None = None
    category: str | None = None
    rule_type: str | None = None
    expression: str | None = None
    description: str | None = None
    priority: int | None = Field(default=None, ge=0)
    status: str | None = None


class RuleRead(RuleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class TopicBase(BaseModel):
    topic_code: str = Field(pattern=r"^[a-z][a-z0-9_]*$", max_length=100)
    topic_name: str = Field(min_length=1, max_length=200)
    description: str = ""
    object_codes: list[str] = Field(default_factory=list)
    metric_codes: list[str] = Field(default_factory=list)
    example_questions: list[str] = Field(default_factory=list)
    status: str = "active"


class TopicCreate(TopicBase):
    pass


class TopicUpdate(BaseModel):
    topic_name: str | None = None
    description: str | None = None
    object_codes: list[str] | None = None
    metric_codes: list[str] | None = None
    example_questions: list[str] | None = None
    status: str | None = None


class TopicRead(TopicBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class KnowledgeSearchResult(BaseModel):
    objects: list[ObjectRead]
    metrics: list[MetricRead]
    rules: list[RuleRead]
    topics: list[TopicRead]
