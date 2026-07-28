export interface MetricItem {
  code: string;
  name: string;
  description: string;
  formula: string;
  category: string;
  synonyms: string[];
}

export interface TableItem {
  name: string;
  displayName: string;
  category: string;
  description: string;
  rows: number;
  columns: Array<{ name: string; type: string; description: string }>;
}

export const defaultMetrics: MetricItem[] = [
  { code: "output_qty", name: "产量", description: "指定范围内的实际生产数量", formula: "SUM(actual_qty)", category: "生产", synonyms: ["生产量", "实际产量"] },
  { code: "process_yield_rate", name: "工序良率", description: "合格数量占实际生产数量的比例", formula: "SUM(qualified_qty) / SUM(actual_qty) × 100%", category: "质量", synonyms: ["合格率", "良品率"] },
  { code: "defect_rate", name: "不良率", description: "不良数量占检验数量的比例", formula: "SUM(defect_qty) / SUM(inspected_qty) × 100%", category: "质量", synonyms: ["缺陷率"] },
  { code: "downtime_minutes", name: "设备停机时长", description: "设备在统计周期内的停机分钟数", formula: "SUM(downtime_minutes)", category: "设备", synonyms: ["停机时间"] },
  { code: "inventory_gap", name: "安全库存缺口", description: "安全库存与当前库存之间的差额", formula: "safety_qty - current_qty", category: "库存", synonyms: ["缺货量", "库存缺口"] },
];

export const tables: TableItem[] = [
  { name: "fact_process_output", displayName: "工序产量表", category: "生产", description: "记录产线、工序每日的实际产量和合格数量", rows: 42860, columns: [
    { name: "production_date", type: "date", description: "生产日期" }, { name: "line_id", type: "bigint", description: "产线标识" },
    { name: "process_name", type: "varchar", description: "工序名称" }, { name: "actual_qty", type: "integer", description: "实际生产数量" },
    { name: "qualified_qty", type: "integer", description: "合格数量" },
  ] },
  { name: "fact_quality_inspection", displayName: "质量检验表", category: "质量", description: "记录产品检验数量、不良数量和缺陷类型", rows: 18920, columns: [
    { name: "inspection_date", type: "date", description: "检验日期" }, { name: "product_name", type: "varchar", description: "产品名称" },
    { name: "inspected_qty", type: "integer", description: "检验数量" }, { name: "defect_qty", type: "integer", description: "不良数量" },
    { name: "defect_type", type: "varchar", description: "缺陷类型" },
  ] },
  { name: "fact_equipment_downtime", displayName: "设备停机表", category: "设备", description: "记录设备停机起止时间、时长和原因", rows: 3260, columns: [
    { name: "equipment_name", type: "varchar", description: "设备名称" }, { name: "started_at", type: "timestamp", description: "停机开始时间" },
    { name: "ended_at", type: "timestamp", description: "恢复时间" }, { name: "downtime_minutes", type: "integer", description: "停机分钟数" },
    { name: "reason", type: "varchar", description: "停机原因" },
  ] },
  { name: "fact_inventory", displayName: "库存表", category: "库存", description: "记录产品当前库存和安全库存", rows: 6820, columns: [
    { name: "record_date", type: "date", description: "记录日期" }, { name: "product_name", type: "varchar", description: "产品名称" },
    { name: "current_qty", type: "integer", description: "当前库存" }, { name: "safety_qty", type: "integer", description: "安全库存" },
  ] },
];

