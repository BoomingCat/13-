from dataclasses import dataclass


@dataclass(frozen=True)
class AnalysisTemplate:
    intent: str
    sql: str
    chart_type: str
    title: str
    conclusion_template: str


PRODUCTION = AnalysisTemplate(
    intent="production_trend",
    sql="""
        SELECT output.production_date AS date, line.line_name,
               SUM(output.actual_qty) AS value
        FROM manufacturing.fact_process_output output
        JOIN manufacturing.dim_production_line line ON line.id = output.line_id
        WHERE output.production_date >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY output.production_date, line.line_name
        ORDER BY output.production_date, line.line_name
    """,
    chart_type="line",
    title="各产线最近7天产量趋势",
    conclusion_template="已完成最近7天产线产量统计，共返回 {count} 条聚合记录。",
)

QUALITY = AnalysisTemplate(
    intent="quality_analysis",
    sql="""
        SELECT process_name AS category,
               ROUND(SUM(qualified_qty) * 100.0 / NULLIF(SUM(actual_qty), 0), 2) AS value
        FROM manufacturing.fact_process_output
        GROUP BY process_name ORDER BY value DESC
    """,
    chart_type="bar",
    title="各工序良率",
    conclusion_template="已完成工序良率统计，共分析 {count} 个工序。",
)

DEFECT = AnalysisTemplate(
    intent="defect_rate_analysis",
    sql="""
        SELECT line.line_name AS category,
               ROUND(SUM(q.defect_qty) * 100.0 / NULLIF(SUM(q.inspected_qty), 0), 2) AS value
        FROM manufacturing.fact_quality_inspection q
        JOIN manufacturing.dim_production_line line ON line.id = q.line_id
        WHERE q.inspection_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY line.line_name
        ORDER BY value DESC
    """,
    chart_type="bar",
    title="最近30天各产线不良率",
    conclusion_template="已完成各产线不良率分析，共分析 {count} 条产线；超过3%的产线需要重点关注。",
)

EQUIPMENT = AnalysisTemplate(
    intent="equipment_analysis",
    sql="""
        SELECT equipment_name AS category, SUM(downtime_minutes) AS value
        FROM manufacturing.fact_equipment_downtime
        GROUP BY equipment_name ORDER BY value DESC
    """,
    chart_type="bar",
    title="设备停机时长",
    conclusion_template="已完成设备停机统计，共分析 {count} 台设备。",
)

INVENTORY = AnalysisTemplate(
    intent="inventory_analysis",
    sql="""
        SELECT product_name AS category, current_qty, safety_qty,
               GREATEST(safety_qty - current_qty, 0) AS value
        FROM manufacturing.fact_inventory
        ORDER BY value DESC
    """,
    chart_type="bar",
    title="产品安全库存缺口",
    conclusion_template="已完成库存检查，共分析 {count} 种产品。",
)


def select_template(question: str) -> AnalysisTemplate:
    if any(word in question for word in ("不良", "缺陷", "次品")):
        return DEFECT
    if any(word in question for word in ("良率", "合格率")):
        return QUALITY
    if any(word in question for word in ("设备", "停机", "故障")):
        return EQUIPMENT
    if any(word in question for word in ("库存", "缺货", "补货")):
        return INVENTORY
    return PRODUCTION
