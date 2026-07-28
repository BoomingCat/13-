from app.modules.metadata.json_repository import JsonMetadataRepository
from app.modules.metadata.schemas import MetadataSearchResult, TableRead


class MetadataNotFoundError(Exception):
    pass


class MetadataService:
    def __init__(self, repository: JsonMetadataRepository) -> None:
        self.repository = repository

    def list_tables(self) -> list[TableRead]:
        return self.repository.list_tables()

    def get_table(self, table_name: str) -> TableRead:
        table = self.repository.get_table(table_name)
        if not table:
            raise MetadataNotFoundError(f"数据表 {table_name} 不存在")
        return table

    def search(self, query: str) -> MetadataSearchResult:
        normalized = query.casefold()
        matched_tables: list[TableRead] = []
        matched_columns: list[dict[str, str]] = []
        for table in self.repository.list_tables():
            table_text = " ".join([
                table.schema_name,
                table.table_name,
                table.display_name or "",
                table.description or "",
                *table.tags,
            ]).casefold()
            if normalized in table_text:
                matched_tables.append(table)
            for column in table.columns:
                column_text = " ".join([
                    column.name,
                    column.description or "",
                    *column.business_terms,
                ]).casefold()
                if normalized in column_text:
                    matched_columns.append({
                        "table": f"{table.schema_name}.{table.table_name}",
                        "column": column.name,
                        "description": column.description or "",
                    })
        return MetadataSearchResult(tables=matched_tables, columns=matched_columns)
