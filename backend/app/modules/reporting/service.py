from datetime import UTC, datetime
from typing import Any


class ReportService:
    """生成可审计的 Markdown 报告；后续由独立渲染器导出 PDF。"""

    def build_markdown(self, *, question: str, sql: str, columns: list[str], rows: list[list[Any]], conclusion: str) -> str:
        header = "| " + " | ".join(columns) + " |"
        divider = "| " + " | ".join("---" for _ in columns) + " |"
        body = "\n".join("| " + " | ".join(str(value) for value in row) + " |" for row in rows[:100])
        return f"""# 企业数据分析报告

- 生成时间：{datetime.now(UTC).isoformat(timespec='seconds')}
- 分析问题：{question}
- 返回记录：{len(rows)}

## 分析结论

{conclusion}

## 结果数据

{header}
{divider}
{body}

## 执行 SQL

```sql
{sql}
```
"""
