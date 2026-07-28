from datetime import UTC, datetime
from time import perf_counter
from typing import Any
from uuid import uuid4

from app.infrastructure.sql.executor import MockQueryExecutor
from app.infrastructure.sql.guard import SQLGuard
from app.modules.sql_execution.repository import SQLExecutionRepository
from app.modules.sql_execution.schemas import SQLExecutionRead, SQLValidateResponse


class SQLExecutionService:
    def __init__(
        self,
        repository: SQLExecutionRepository,
        *,
        max_rows: int = 1000,
        allowed_schemas: set[str] | None = None,
    ) -> None:
        self.repository = repository
        self.guard = SQLGuard(allowed_schemas=allowed_schemas, max_rows=max_rows)
        self.executor = MockQueryExecutor(
            max_rows=max_rows,
            allowed_schemas=allowed_schemas,
        )

    def validate(self, sql: str) -> SQLValidateResponse:
        result = self.guard.validate(sql)
        return SQLValidateResponse(
            valid=result.valid,
            normalized_sql=result.normalized_sql,
            errors=result.errors,
        )

    async def execute(self, sql: str, parameters: dict[str, Any]) -> SQLExecutionRead:
        started = perf_counter()
        execution_id = str(uuid4())
        try:
            normalized, columns, rows = await self.executor.execute(sql, parameters)
            record = {
                "id": execution_id,
                "sql": sql,
                "normalized_sql": normalized,
                "status": "completed",
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "duration_ms": round((perf_counter() - started) * 1000, 3),
                "error": None,
                "created_at": datetime.now(UTC).isoformat(),
            }
        except ValueError as error:
            validation = self.guard.validate(sql)
            record = {
                "id": execution_id,
                "sql": sql,
                "normalized_sql": validation.normalized_sql or "",
                "status": "rejected",
                "columns": [],
                "rows": [],
                "row_count": 0,
                "duration_ms": round((perf_counter() - started) * 1000, 3),
                "error": str(error),
                "created_at": datetime.now(UTC).isoformat(),
            }
        self.repository.save(record)
        return SQLExecutionRead.model_validate(record)
