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
        SELECT output.stat_date AS date, line.line_name,
               SUM(output.good_qty + output.defect_qty) AS value
        FROM manufacturing.mes_process_output output
        JOIN manufacturing.dim_production_line line ON line.line_id = output.line_id
        WHERE output.stat_date >= (
            SELECT MAX(stat_date) FROM manufacturing.mes_process_output
        ) - INTERVAL '6 days'
        GROUP BY output.stat_date, line.line_name
        ORDER BY output.stat_date, line.line_name
    """,
    chart_type="line",
    title="各产线最近7天产量趋势",
    conclusion_template="已完成最近7天产线产量统计，共返回 {count} 条聚合记录。",
)

QUALITY = AnalysisTemplate(
    intent="quality_analysis",
    sql="""
        SELECT process.process_name AS category,
               ROUND(SUM(output.good_qty) * 100.0 / NULLIF(SUM(output.input_qty), 0), 2) AS value
        FROM manufacturing.mes_process_output output
        JOIN manufacturing.dim_process process ON process.process_id = output.process_id
        GROUP BY process.process_name ORDER BY value DESC
    """,
    chart_type="bar",
    title="各工序良率",
    conclusion_template="已完成工序良率统计，共分析 {count} 个工序。",
)

DEFECT = AnalysisTemplate(
    intent="defect_rate_analysis",
    sql="""
        SELECT line.line_name AS category,
               ROUND(SUM(q.defect_qty) * 100.0 / NULLIF(SUM(q.sample_qty), 0), 2) AS value
        FROM manufacturing.qms_inspection q
        JOIN manufacturing.mes_work_order work_order
          ON work_order.work_order_id = q.work_order_id
        JOIN manufacturing.dim_production_line line
          ON line.line_id = work_order.line_id
        WHERE q.inspection_date >= (
            SELECT MAX(inspection_date) FROM manufacturing.qms_inspection
        ) - INTERVAL '29 days'
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
        FROM manufacturing.eqp_downtime_record downtime
        JOIN manufacturing.dim_equipment equipment
          ON equipment.equipment_id = downtime.equipment_id
        GROUP BY equipment.equipment_name ORDER BY value DESC
    """,
    chart_type="bar",
    title="设备停机时长",
    conclusion_template="已完成设备停机统计，共分析 {count} 台设备。",
)

INVENTORY = AnalysisTemplate(
    intent="inventory_analysis",
    sql="""
        SELECT product.product_name AS category,
               SUM(inventory.available_qty) AS current_qty,
               SUM(inventory.safety_stock_qty) AS safety_qty,
               GREATEST(
                   SUM(inventory.safety_stock_qty) - SUM(inventory.available_qty), 0
               ) AS value
        FROM manufacturing.inv_inventory_snapshot inventory
        JOIN manufacturing.dim_product product
          ON product.product_id = inventory.product_id
        WHERE inventory.snapshot_date = (
            SELECT MAX(snapshot_date) FROM manufacturing.inv_inventory_snapshot
        )
        GROUP BY product.product_name
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
