from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.sql.guard import SQLGuard


class ReadOnlyQueryExecutor:
    def __init__(
        self,
        session: AsyncSession,
        max_rows: int = 1000,
        allowed_schemas: set[str] | None = None,
    ) -> None:
        self.session = session
        self.guard = SQLGuard(allowed_schemas=allowed_schemas, max_rows=max_rows)

    async def execute(self, sql: str, parameters: dict[str, Any] | None = None) -> tuple[str, list[str], list[list[Any]]]:
        validation = self.guard.validate(sql)
        if not validation.valid or not validation.normalized_sql:
            raise ValueError("; ".join(validation.errors))
        result = await self.session.execute(text(validation.normalized_sql), parameters or {})
        columns = list(result.keys())
        rows = [[self._json_value(value) for value in row] for row in result.fetchall()]
        return validation.normalized_sql, columns, rows

    @staticmethod
    def _json_value(value: Any) -> Any:
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        return value


class MockQueryExecutor:
    """开发阶段执行器：仍进行真实 SQL 安全校验，但从固定样例返回结果。"""

    def __init__(
        self,
        max_rows: int = 1000,
        allowed_schemas: set[str] | None = None,
    ) -> None:
        self.guard = SQLGuard(allowed_schemas=allowed_schemas, max_rows=max_rows)

    async def execute(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> tuple[str, list[str], list[list[Any]]]:
        validation = self.guard.validate(sql)
        if not validation.valid or not validation.normalized_sql:
            raise ValueError("; ".join(validation.errors))
        normalized = validation.normalized_sql
        lowered = normalized.lower()
        if "fact_quality_inspection" in lowered:
            return normalized, ["category", "value"], [["产线B", 4.8], ["产线C", 3.2], ["产线A", 2.1]]
        if "fact_equipment_downtime" in lowered:
            return normalized, ["category", "value"], [["切割机-01", 320], ["冲压机-02", 185], ["装配机-03", 90]]
        if "fact_inventory" in lowered:
            return normalized, ["category", "current_qty", "safety_qty", "value"], [
                ["轴承A", 80, 150, 70],
                ["齿轮B", 120, 160, 40],
                ["密封圈C", 300, 200, 0],
            ]
        if "qualified_qty" in lowered:
            return normalized, ["category", "value"], [["装配", 98.2], ["加工", 96.7], ["检验", 94.5]]
        return normalized, ["date", "line_name", "value"], [
            ["2026-07-19", "产线A", 980],
            ["2026-07-19", "产线B", 920],
            ["2026-07-20", "产线A", 1020],
            ["2026-07-20", "产线B", 960],
        ]
