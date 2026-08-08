# 前端字段需求清单 V1

更新时间：2026-08-08

## 智能问析主接口

`POST /api/v1/analysis/query`

请求字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| question | string | 是 | 用户自然语言问题，长度 2～1000 |
| conversation_id | UUID | 否 | 后续多轮对话标识 |

响应字段：

| 字段 | 前端用途 |
|---|---|
| task_id | 分析任务编号与历史记录主键 |
| conversation_id | 多轮对话标识 |
| question | 回显用户问题 |
| intent | 展示识别出的分析类型 |
| plan | 调试和执行计划展示 |
| sql | 只读 SQL 展示；可能为空 |
| columns | 结果表格表头 |
| rows | 结果表格数据，顺序必须与 columns 一致 |
| conclusion | 分析结论卡片 |
| chart | ECharts 图表协议，使用 type、title、option |
| steps | Agent 执行轨迹 |

## 前端约束

- 不假定列名固定，表格完全按照 `columns + rows` 渲染。
- `chart` 为空时隐藏图表，不把它视为接口错误。
- `sql` 为空时隐藏 SQL 或显示“本次未生成 SQL”。
- 请求超时时间暂定 15 秒。
- 优先使用真实 API；API 失败时允许切换本地 Mock，并明确标注数据来源。

## 当前场景

1. 生产：最近 7 天各产线产量趋势。
2. 质量：各工序良率、产线不良率。
3. 设备：设备停机时长。
4. 库存：库存缺口与安全库存。

