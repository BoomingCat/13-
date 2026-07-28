from typing import ClassVar

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class MetadataTable(Base):
    __tablename__ = "metadata_tables"
    __table_args__: ClassVar[dict[str, str]] = {"schema": "fwwb"}
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    schema_name: Mapped[str] = mapped_column(String(100), index=True)
    table_name: Mapped[str] = mapped_column(String(200), index=True)
    display_name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(50))
    row_estimate: Mapped[int] = mapped_column(BigInteger, default=0)
    columns: Mapped[list["MetadataColumn"]] = relationship(back_populates="table", cascade="all, delete-orphan")


class MetadataColumn(Base):
    __tablename__ = "metadata_columns"
    __table_args__: ClassVar[dict[str, str]] = {"schema": "fwwb"}
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    table_id: Mapped[int] = mapped_column(ForeignKey("fwwb.metadata_tables.id", ondelete="CASCADE"))
    column_name: Mapped[str] = mapped_column(String(200))
    data_type: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    sample_values: Mapped[list[str]] = mapped_column(JSONB, default=list)
    is_sensitive: Mapped[bool] = mapped_column(default=False)
    table: Mapped[MetadataTable] = relationship(back_populates="columns")
