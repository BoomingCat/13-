from collections import defaultdict
from typing import Any

from app.modules.analysis.schemas import AgentStep, AnalysisRequest, AnalysisResponse, ChartSpec
from app.modules.analysis.planner import RuleBasedPlanner
from app.modules.analysis.templates import AnalysisTemplate, select_template


class AgentService:
    """不依赖大模型的分析闭环；未来可将模板选择替换为 DeepSeek 规划结果。"""

    def __init__(self, executor: Any) -> None:
        self.executor = executor

    async def analyze(self, payload: AnalysisRequest) -> AnalysisResponse:
        template = select_template(payload.question)
        plan = RuleBasedPlanner().plan(payload.question)
        sql, columns, rows = await self.executor.execute(template.sql)
        response = AnalysisResponse(
            question=payload.question,
            intent=template.intent,
            plan={
                "intent": plan.intent,
                "metric_codes": list(plan.metric_codes),
                "tables": list(plan.tables),
                "steps": list(plan.steps),
            },
            sql=sql,
            columns=columns,
            rows=rows,
            conclusion=template.conclusion_template.format(count=len(rows)),
            chart=self._chart(template, columns, rows),
            steps=[
                AgentStep(name="意图识别", status="completed", detail=f"规则规划器识别为 {template.intent}"),
                AgentStep(name="指标匹配", status="completed", detail="从业务指标目录匹配计算口径"),
                AgentStep(name="SQL生成", status="completed", detail="选择受控分析模板"),
                AgentStep(name="安全校验", status="completed", detail="通过只读、Schema 白名单和行数限制检查"),
                AgentStep(name="数据执行", status="completed", detail=f"查询执行器返回 {len(rows)} 行"),
            ],
        )
        if payload.conversation_id:
            response.conversation_id = payload.conversation_id
        return response

    def _chart(self, template: AnalysisTemplate, columns: list[str], rows: list[list[Any]]) -> ChartSpec:
        if template.chart_type == "line" and len(columns) >= 3:
            series_data: dict[str, list[list[Any]]] = defaultdict(list)
            for row in rows:
                series_data[str(row[1])].append([row[0], row[2]])
            option = {
                "tooltip": {"trigger": "axis"},
                "legend": {"data": list(series_data)},
                "xAxis": {"type": "category", "data": sorted({row[0] for row in rows})},
                "yAxis": {"type": "value"},
                "series": [{"name": name, "type": "line", "smooth": True, "data": [item[1] for item in values]} for name, values in series_data.items()],
            }
        else:
            option = {
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": [row[0] for row in rows]},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar", "data": [row[-1] for row in rows]}],
            }
        return ChartSpec(type=template.chart_type, title=template.title, option=option)
