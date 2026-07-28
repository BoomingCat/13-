import json
from pathlib import Path
from typing import Any

from app.modules.metadata.schemas import DataSourceRead, RelationRead, TableRead


class JsonMetadataRepository:
    def __init__(self, data_dir: Path) -> None:
        self.metadata_dir = data_dir / "metadata"

    def _load(self, name: str) -> list[dict[str, Any]]:
        path = self.metadata_dir / name
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def list_tables(self) -> list[TableRead]:
        return [TableRead.model_validate(item) for item in self._load("tables.json")]

    def get_table(self, table_name: str) -> TableRead | None:
        return next(
            (
                table for table in self.list_tables()
                if table.table_name == table_name
                or f"{table.schema_name}.{table.table_name}" == table_name
            ),
            None,
        )

    def list_relations(self) -> list[RelationRead]:
        return [RelationRead.model_validate(item) for item in self._load("relations.json")]

    def list_sources(self) -> list[DataSourceRead]:
        return [DataSourceRead.model_validate(item) for item in self._load("sources.json")]
