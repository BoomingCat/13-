from dataclasses import dataclass


@dataclass(frozen=True)
class AnalysisPlan:
    intent: str
    metric_codes: tuple[str, ...]
    tables: tuple[str, ...]
    steps: tuple[str, ...]


class RuleBasedPlanner:
    """DeepSeek 未启用前使用的确定性规划器。"""

    def plan(self, question: str) -> AnalysisPlan:
        if any(word in question for word in ("不良", "缺陷", "次品")):
            metric_codes = ("defect_rate",)
            tables = (
                "manufacturing.qms_inspection",
                "manufacturing.mes_work_order",
                "manufacturing.dim_production_line",
            )
        elif any(word in question for word in ("良率", "合格率")):
            metric_codes = ("process_yield_rate",)
            tables = ("manufacturing.mes_process_output", "manufacturing.dim_process")
        elif any(word in question for word in ("设备", "停机", "故障")):
            metric_codes = ("downtime_minutes",)
            tables = ("manufacturing.eqp_downtime_record", "manufacturing.dim_equipment")
        elif any(word in question for word in ("库存", "缺货", "补货")):
            metric_codes = ("inventory_gap",)
            tables = ("manufacturing.inv_inventory_snapshot", "manufacturing.dim_product")
        else:
            metric_codes = ("output_qty",)
            tables = ("manufacturing.mes_process_output", "manufacturing.dim_production_line")
        return AnalysisPlan(
            intent="manufacturing_data_analysis",
            metric_codes=metric_codes,
            tables=tables,
            steps=("识别意图", "匹配业务指标", "定位数据表", "生成安全查询", "展示分析结果"),
        )
