from math import sqrt
from statistics import fmean
from typing import Any

from app.modules.analytics.schemas import (
    AnalysisRowsResponse,
    ColumnSummary,
    SummaryResponse,
)


class AnalyticsService:
    @staticmethod
    def _index(columns: list[str], name: str) -> int:
        if name not in columns:
            raise ValueError(f"字段 {name} 不存在")
        return columns.index(name)

    def summarize(
        self,
        columns: list[str],
        rows: list[list[Any]],
        numeric_columns: list[str],
    ) -> SummaryResponse:
        targets = numeric_columns or [
            name for index, name in enumerate(columns)
            if any(index < len(row) and isinstance(row[index], (int, float)) for row in rows)
        ]
        summaries: list[ColumnSummary] = []
        for name in targets:
            index = self._index(columns, name)
            values = [
                float(row[index]) for row in rows
                if index < len(row) and isinstance(row[index], (int, float))
            ]
            summaries.append(ColumnSummary(
                column=name,
                count=len(values),
                missing=len(rows) - len(values),
                minimum=min(values) if values else None,
                maximum=max(values) if values else None,
                mean=fmean(values) if values else None,
                total=sum(values) if values else None,
            ))
        return SummaryResponse(row_count=len(rows), summaries=summaries)

    def rank(
        self,
        columns: list[str],
        rows: list[list[Any]],
        category_column: str,
        value_column: str,
        descending: bool,
        limit: int,
    ) -> AnalysisRowsResponse:
        category_index = self._index(columns, category_column)
        value_index = self._index(columns, value_column)
        selected = sorted(
            rows,
            key=lambda row: float(row[value_index]),
            reverse=descending,
        )[:limit]
        return AnalysisRowsResponse(
            columns=[category_column, value_column, "rank"],
            rows=[
                [row[category_index], row[value_index], rank]
                for rank, row in enumerate(selected, start=1)
            ],
        )

    def anomalies(
        self,
        columns: list[str],
        rows: list[list[Any]],
        value_column: str,
        threshold: float,
    ) -> AnalysisRowsResponse:
        value_index = self._index(columns, value_column)
        values = [float(row[value_index]) for row in rows]
        if len(values) < 2:
            return AnalysisRowsResponse(columns=[*columns, "z_score"], rows=[])
        mean = fmean(values)
        deviation = sqrt(sum((value - mean) ** 2 for value in values) / len(values))
        if deviation == 0:
            return AnalysisRowsResponse(columns=[*columns, "z_score"], rows=[])
        result = []
        for row, value in zip(rows, values, strict=True):
            score = (value - mean) / deviation
            if abs(score) >= threshold:
                result.append([*row, round(score, 4)])
        return AnalysisRowsResponse(columns=[*columns, "z_score"], rows=result)
