from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class BusinessMetric(Base):
    __tablename__ = "business_metrics"
    __table_args__ = {"schema": "fwwb"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    metric_code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    metric_name: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    formula_expression: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50), default="生产")
    unit: Mapped[str | None] = mapped_column(String(30))
    time_field: Mapped[str | None] = mapped_column(String(100))
    source_tables: Mapped[list[str]] = mapped_column(JSONB, default=list)
    dimension_fields: Mapped[list[str]] = mapped_column(JSONB, default=list)
    synonyms: Mapped[list[str]] = mapped_column(JSONB, default=list)
    version: Mapped[int] = mapped_column(default=1)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class BusinessObject(Base):
    __tablename__ = "business_objects"
    __table_args__ = {"schema": "fwwb"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    object_code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    object_name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(50), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    source_table: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class BusinessRule(Base):
    __tablename__ = "business_rules"
    __table_args__ = {"schema": "fwwb"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    rule_code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    rule_name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(50), index=True)
    rule_type: Mapped[str] = mapped_column(String(50))
    expression: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text, default="")
    priority: Mapped[int] = mapped_column(Integer, default=100)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AnalysisTopic(Base):
    __tablename__ = "analysis_topics"
    __table_args__ = {"schema": "fwwb"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    topic_code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    topic_name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    object_codes: Mapped[list[str]] = mapped_column(JSONB, default=list)
    metric_codes: Mapped[list[str]] = mapped_column(JSONB, default=list)
    example_questions: Mapped[list[str]] = mapped_column(JSONB, default=list)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
