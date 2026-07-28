from typing import Any, TypedDict


class AnalysisState(TypedDict, total=False):
    question: str
    rewritten_question: str
    intent: str
    selected_metrics: list[str]
    selected_tables: list[str]
    plan: list[dict[str, Any]]
    generated_sql: str
    generated_code: str
    execution_result: dict[str, Any]
    chart_spec: dict[str, Any]
    conclusion: str
    errors: list[str]
    audit_trace: list[dict[str, Any]]
