from collections import defaultdict
from datetime import date, timedelta
from typing import Any

from app.infrastructure.sql.guard import SQLGuard
from app.modules.datasets.repository import CsvDatasetRepository


class CsvAnalysisExecutor:
    """在CSV开发数据上执行受控的制造业指标模板。"""

    source_name = "CSV数据执行器"

    def __init__(
        self,
        repository: CsvDatasetRepository,
        max_rows: int = 1000,
        allowed_schemas: set[str] | None = None,
    ) -> None:
        self.repository = repository
        self.guard = SQLGuard(allowed_schemas=allowed_schemas, max_rows=max_rows)

    def _rows(self, name: str) -> list[dict[str, Any]]:
        return self.repository.rows(name, 0, 100_000).rows

    async def execute(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> tuple[str, list[str], list[list[Any]]]:
        del parameters
        validation = self.guard.validate(sql)
        if not validation.valid or not validation.normalized_sql:
            raise ValueError("; ".join(validation.errors))
        normalized = validation.normalized_sql
        lowered = normalized.casefold()
        if "qms_inspection" in lowered:
            columns, rows = self._defect_rate()
        elif "eqp_downtime_record" in lowered:
            columns, rows = self._equipment_downtime()
        elif "inv_inventory_snapshot" in lowered:
            columns, rows = self._inventory_gap()
        elif "dim_process" in lowered:
            columns, rows = self._process_yield()
        elif "mes_process_output" in lowered:
            columns, rows = self._production_trend()
        else:
            raise ValueError("当前CSV模式不支持此查询模板")
        return normalized, columns, rows

    def _production_trend(self) -> tuple[list[str], list[list[Any]]]:
        outputs = self._rows("mes_process_output")
        lines = {row["line_id"]: row["line_name"] for row in self._rows("dim_production_line")}
        latest = max(date.fromisoformat(str(row["stat_date"])) for row in outputs)
        cutoff = latest - timedelta(days=6)
        grouped: dict[tuple[str, str], int] = defaultdict(int)
        for row in outputs:
            stat_date = date.fromisoformat(str(row["stat_date"]))
            if stat_date >= cutoff:
                grouped[(str(row["stat_date"]), lines.get(row["line_id"], row["line_id"]))] += (
                    int(row["good_qty"]) + int(row["defect_qty"])
                )
        rows = [[day, line, value] for (day, line), value in sorted(grouped.items())]
        return ["date", "line_name", "value"], rows

    def _process_yield(self) -> tuple[list[str], list[list[Any]]]:
        processes = {row["process_id"]: row["process_name"] for row in self._rows("dim_process")}
        totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])
        for row in self._rows("mes_process_output"):
            process = processes.get(row["process_id"], row["process_id"])
            totals[process][0] += int(row["good_qty"])
            totals[process][1] += int(row["input_qty"])
        rows = [
            [process, round(good * 100 / input_qty, 2) if input_qty else 0.0]
            for process, (good, input_qty) in totals.items()
        ]
        rows.sort(key=lambda row: row[1], reverse=True)
        return ["category", "value"], rows

    def _defect_rate(self) -> tuple[list[str], list[list[Any]]]:
        inspections = self._rows("qms_inspection")
        orders = {row["work_order_id"]: row["line_id"] for row in self._rows("mes_work_order")}
        lines = {row["line_id"]: row["line_name"] for row in self._rows("dim_production_line")}
        latest = max(date.fromisoformat(str(row["inspection_date"])) for row in inspections)
        cutoff = latest - timedelta(days=29)
        totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])
        for row in inspections:
            if date.fromisoformat(str(row["inspection_date"])) < cutoff:
                continue
            line_id = orders.get(row["work_order_id"], "unknown")
            line_name = lines.get(line_id, line_id)
            totals[line_name][0] += int(row["defect_qty"])
            totals[line_name][1] += int(row["sample_qty"])
        rows = [
            [line, round(defects * 100 / samples, 2) if samples else 0.0]
            for line, (defects, samples) in totals.items()
        ]
        rows.sort(key=lambda row: row[1], reverse=True)
        return ["category", "value"], rows

    def _equipment_downtime(self) -> tuple[list[str], list[list[Any]]]:
        equipment = {
            row["equipment_id"]: row["equipment_name"]
            for row in self._rows("dim_equipment")
        }
        totals: dict[str, int] = defaultdict(int)
        for row in self._rows("eqp_downtime_record"):
            name = equipment.get(row["equipment_id"], row["equipment_id"])
            totals[name] += int(row["downtime_minutes"])
        rows = [[name, minutes] for name, minutes in totals.items()]
        rows.sort(key=lambda row: row[1], reverse=True)
        return ["category", "value"], rows

    def _inventory_gap(self) -> tuple[list[str], list[list[Any]]]:
        snapshots = self._rows("inv_inventory_snapshot")
        products = {row["product_id"]: row["product_name"] for row in self._rows("dim_product")}
        latest = max(str(row["snapshot_date"]) for row in snapshots)
        totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])
        for row in snapshots:
            if str(row["snapshot_date"]) != latest:
                continue
            name = products.get(row["product_id"], row["product_id"])
            totals[name][0] += int(row["available_qty"])
            totals[name][1] += int(row["safety_stock_qty"])
        rows = [
            [name, current, safety, max(safety - current, 0)]
            for name, (current, safety) in totals.items()
        ]
        rows.sort(key=lambda row: row[-1], reverse=True)
        return ["category", "current_qty", "safety_qty", "value"], rows
