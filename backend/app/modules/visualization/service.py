from typing import Any

from app.modules.visualization.schemas import ChartResponse


class VisualizationService:
    def recommend(self, columns: list[str], rows: list[list[Any]]) -> tuple[str, str]:
        if len(rows) == 1 and len(columns) <= 2:
            return "card", "单行少量指标适合使用指标卡。"
        first_name = columns[0].lower()
        if any(word in first_name for word in ("date", "time", "日期", "时间")):
            return "line", "第一列是时间字段，适合展示趋势。"
        if len(rows) <= 8 and len(columns) == 2:
            return "pie", "分类数量较少且只有一个数值指标，适合展示构成。"
        if len(columns) >= 2:
            return "bar", "分类与数值对比适合使用柱状图。"
        return "table", "当前数据结构更适合表格展示。"

    def build(
        self,
        title: str,
        columns: list[str],
        rows: list[list[Any]],
        chart_type: str | None,
        category_column: str | None,
        value_columns: list[str],
    ) -> ChartResponse:
        recommended, reason = self.recommend(columns, rows)
        selected = chart_type or recommended
        category = category_column or columns[0]
        category_index = columns.index(category)
        values = value_columns or [
            column for index, column in enumerate(columns)
            if index != category_index
            and any(index < len(row) and isinstance(row[index], (int, float)) for row in rows)
        ]
        if selected == "table":
            option: dict[str, Any] = {"columns": columns, "rows": rows}
        elif selected == "card":
            option = {
                "items": [
                    {"name": column, "value": rows[0][index] if rows else None}
                    for index, column in enumerate(columns)
                ]
            }
        elif selected == "pie":
            value = values[0] if values else columns[-1]
            value_index = columns.index(value)
            option = {
                "tooltip": {"trigger": "item"},
                "series": [{
                    "name": value,
                    "type": "pie",
                    "data": [
                        {"name": row[category_index], "value": row[value_index]}
                        for row in rows
                    ],
                }],
            }
        else:
            series_type = "scatter" if selected == "scatter" else selected
            option = {
                "tooltip": {"trigger": "axis"},
                "legend": {"data": values},
                "xAxis": {"type": "category", "data": [row[category_index] for row in rows]},
                "yAxis": {"type": "value"},
                "series": [
                    {
                        "name": value,
                        "type": series_type,
                        "data": [row[columns.index(value)] for row in rows],
                    }
                    for value in values
                ],
            }
        return ChartResponse(chart_type=selected, title=title, option=option, reason=reason)
