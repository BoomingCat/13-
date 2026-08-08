import json
from collections import defaultdict
from typing import Any

from app.infrastructure.llm.base import ChatMessage, LLMClient
from app.modules.analysis.planner import RuleBasedPlanner
from app.modules.analysis.schemas import (
    AgentStep,
    AnalysisRequest,
    AnalysisResponse,
    ChartSpec,
)
from app.modules.analysis.templates import AnalysisTemplate, select_template


class AgentService:
    """不依赖大模型的分析闭环；未来可将模板选择替换为 DeepSeek 规划结果。"""

    def __init__(self, executor: Any, llm_client: LLMClient | None = None) -> None:
        self.executor = executor
        self.llm_client = llm_client

    async def analyze(self, payload: AnalysisRequest) -> AnalysisResponse:
        template = select_template(payload.question)
        plan = RuleBasedPlanner().plan(payload.question)
        sql, columns, rows = await self.executor.execute(template.sql)
        default_conclusion = template.conclusion_template.format(count=len(rows))
        conclusion, llm_step = await self._build_conclusion(
            question=payload.question,
            columns=columns,
            rows=rows,
            default_conclusion=default_conclusion,
        )
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
            conclusion=conclusion,
            chart=self._chart(template, columns, rows),
            steps=[
                AgentStep(name="意图识别", status="completed", detail=f"规则规划器识别为 {template.intent}"),
                AgentStep(name="指标匹配", status="completed", detail="从业务指标目录匹配计算口径"),
                AgentStep(name="SQL生成", status="completed", detail="选择受控分析模板"),
                AgentStep(name="安全校验", status="completed", detail="通过只读、Schema 白名单和行数限制检查"),
                AgentStep(
                    name="数据执行",
                    status="completed",
                    detail=f"{getattr(self.executor, 'source_name', '查询执行器')}返回 {len(rows)} 行",
                ),
                llm_step,
            ],
        )
        if payload.conversation_id:
            response.conversation_id = payload.conversation_id
        return response

    async def _build_conclusion(
        self,
        *,
        question: str,
        columns: list[str],
        rows: list[list[Any]],
        default_conclusion: str,
    ) -> tuple[str, AgentStep]:
        if self.llm_client is None:
            return default_conclusion, AgentStep(
                name="大模型解释",
                status="completed",
                detail="DeepSeek未启用，使用规则结论",
            )

        sample = {"columns": columns, "rows": rows[:20], "total_rows": len(rows)}
        messages = [
            ChatMessage(
                role="system",
                content=(
                    "你是制造业数据分析助手。只能依据提供的数据生成中文结论，"
                    "不得编造未提供的数字。用2到4句话概括趋势、异常和建议。"
                ),
            ),
            ChatMessage(
                role="user",
                content=(
                    f"用户问题：{question}\n"
                    f"规则结论：{default_conclusion}\n"
                    f"分析结果：{json.dumps(sample, ensure_ascii=False, default=str)}"
                ),
            ),
        ]
        try:
            result = await self.llm_client.chat(messages, temperature=0.1)
            return result.content.strip(), AgentStep(
                name="大模型解释",
                status="completed",
                detail=f"DeepSeek已生成分析解释（模型：{result.model}）",
            )
        except RuntimeError:
            return default_conclusion, AgentStep(
                name="大模型解释",
                status="failed",
                detail="DeepSeek调用失败，已安全回退规则结论",
            )

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
