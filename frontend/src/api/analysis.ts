export interface AgentStep {
  name: string;
  status: string;
  detail: string;
}

export interface AnalysisResult {
  task_id: string;
  question: string;
  intent: string;
  sql?: string;
  columns: string[];
  rows: Array<Array<string | number>>;
  conclusion: string;
  chart?: { title: string; type: string; option: Record<string, unknown> };
  steps: AgentStep[];
}

export async function analyze(question: string): Promise<AnalysisResult> {
  // 当前阶段完全使用浏览器本地 Mock，不调用 Agent、后端或大模型 API。
  await new Promise((resolve) => window.setTimeout(resolve, 500));
  if (/良率|合格率|不良/.test(question)) return qualityResult(question);
  if (/停机|设备|故障/.test(question)) return equipmentResult(question);
  if (/库存|缺货|安全库存/.test(question)) return inventoryResult(question);
  const dates = ["07-15", "07-16", "07-17", "07-18", "07-19", "07-20", "07-21"];
  const firstLine = [930, 960, 910, 990, 1020, 1040, 1080];
  const secondLine = [810, 840, 860, 830, 880, 900, 920];

  return {
    task_id: crypto.randomUUID(),
    question,
    intent: "production_trend_analysis",
    sql: "SELECT production_date, line_name, SUM(actual_qty) AS output_qty\nFROM manufacturing.fact_process_output\nWHERE production_date >= CURRENT_DATE - INTERVAL '7 days'\nGROUP BY production_date, line_name\nORDER BY production_date, line_name LIMIT 1000;",
    columns: ["日期", "一号产线", "二号产线"],
    rows: dates.map((date, index) => [date, firstLine[index], secondLine[index]]),
    conclusion: "一号产线总体呈上升趋势；二号产线波动较小，最近三天持续增长。当前结果来自前端本地模拟数据。",
    chart: {
      type: "line",
      title: "各产线最近7天产量趋势",
      option: {
        tooltip: { trigger: "axis" },
        legend: { data: ["一号产线", "二号产线"] },
        xAxis: { type: "category", data: dates },
        yAxis: { type: "value", name: "产量" },
        series: [
          { name: "一号产线", type: "line", smooth: true, data: firstLine },
          { name: "二号产线", type: "line", smooth: true, data: secondLine },
        ],
      },
    },
    steps: [
      { name: "意图识别", status: "completed", detail: "本地模拟：识别为制造业趋势分析" },
      { name: "指标匹配", status: "completed", detail: "本地模拟：匹配产量指标与产线维度" },
      { name: "数据处理", status: "completed", detail: "读取前端内置演示数据" },
      { name: "图表生成", status: "completed", detail: "在浏览器中生成 ECharts 配置" },
    ],
  };
}

function base(question: string, intent: string, sql: string, conclusion: string, columns: string[], rows: Array<Array<string | number>>, chart: AnalysisResult["chart"]): AnalysisResult {
  return {
    task_id: crypto.randomUUID(), question, intent, sql, conclusion, columns, rows, chart,
    steps: [
      { name: "意图识别", status: "completed", detail: `本地规则识别为 ${intent}` },
      { name: "指标匹配", status: "completed", detail: "从业务指标目录匹配指标口径" },
      { name: "数据定位", status: "completed", detail: "完成数据表及字段映射" },
      { name: "安全校验", status: "completed", detail: "SQL 只读检查通过并限制返回行数" },
      { name: "结果展示", status: "completed", detail: "使用本地演示数据生成图表和结论" },
    ],
  };
}

function qualityResult(question: string): AnalysisResult {
  const names = ["切割", "焊接", "装配", "包装"], values = [98.6, 97.2, 95.8, 99.1];
  return base(question, "质量分析", "SELECT process_name, SUM(qualified_qty) * 100.0 / NULLIF(SUM(actual_qty), 0) AS yield_rate\nFROM manufacturing.fact_process_output\nGROUP BY process_name LIMIT 1000;", "装配工序良率最低，为 95.8%，建议重点检查装配参数与人员操作记录。", ["工序", "良率(%)"], names.map((name, i) => [name, values[i]]), { type: "bar", title: "各工序良率", option: { tooltip: {}, xAxis: { type: "category", data: names }, yAxis: { type: "value", min: 90, name: "%" }, series: [{ type: "bar", data: values, itemStyle: { color: "#18a999" } }] } });
}

function equipmentResult(question: string): AnalysisResult {
  const names = ["装配机-01", "装配机-02", "检测机-01", "包装机-01"], values = [125, 68, 42, 96];
  return base(question, "设备分析", "SELECT equipment_name, SUM(downtime_minutes) AS total_minutes\nFROM manufacturing.fact_equipment_downtime\nGROUP BY equipment_name ORDER BY total_minutes DESC LIMIT 1000;", "装配机-01 停机时间最高，共 125 分钟，应优先排查其重复故障原因。", ["设备", "停机分钟"], names.map((name, i) => [name, values[i]]), { type: "bar", title: "设备停机时长", option: { tooltip: {}, xAxis: { type: "category", data: names }, yAxis: { type: "value", name: "分钟" }, series: [{ type: "bar", data: values, itemStyle: { color: "#f29d49" } }] } });
}

function inventoryResult(question: string): AnalysisResult {
  const names = ["产品A", "产品B", "产品C", "产品D"], current = [520, 260, 410, 180], safety = [300, 300, 350, 280];
  return base(question, "库存分析", "SELECT product_name, current_qty, safety_qty\nFROM manufacturing.fact_inventory\nWHERE current_qty < safety_qty ORDER BY current_qty LIMIT 1000;", "产品B和产品D低于安全库存，其中产品D缺口为100件，建议优先补货。", ["产品", "当前库存", "安全库存"], names.map((name, i) => [name, current[i], safety[i]]), { type: "bar", title: "当前库存与安全库存", option: { tooltip: { trigger: "axis" }, legend: { data: ["当前库存", "安全库存"] }, xAxis: { type: "category", data: names }, yAxis: { type: "value" }, series: [{ name: "当前库存", type: "bar", data: current }, { name: "安全库存", type: "bar", data: safety }] } });
}
