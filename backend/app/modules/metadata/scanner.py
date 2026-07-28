from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.metadata.schemas import ColumnRead, TableRead


class MetadataScanner:
    """从 PostgreSQL 系统目录读取业务 Schema，不修改业务表。"""

    def __init__(self, session: AsyncSession, allowed_schemas: set[str] | None = None) -> None:
        self.session = session
        self.allowed_schemas = allowed_schemas or {"manufacturing"}

    async def scan(self) -> list[TableRead]:
        sql = text("""
            SELECT c.table_schema, c.table_name, c.column_name, c.data_type,
                   pgd.description AS column_description
            FROM information_schema.columns c
            LEFT JOIN pg_catalog.pg_statio_all_tables st
              ON st.schemaname = c.table_schema AND st.relname = c.table_name
            LEFT JOIN pg_catalog.pg_description pgd
              ON pgd.objoid = st.relid AND pgd.objsubid = c.ordinal_position
            WHERE c.table_schema = ANY(:schemas)
            ORDER BY c.table_schema, c.table_name, c.ordinal_position
        """)
        rows = (await self.session.execute(sql, {"schemas": list(self.allowed_schemas)})).mappings()
        grouped: dict[tuple[str, str], list[ColumnRead]] = {}
        for row in rows:
            key = (row["table_schema"], row["table_name"])
            grouped.setdefault(key, []).append(ColumnRead(
                name=row["column_name"],
                data_type=row["data_type"],
                description=row["column_description"],
            ))
        return [TableRead(schema_name=schema, table_name=table, columns=columns) for (schema, table), columns in grouped.items()]
