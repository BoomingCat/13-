# A07 前后端接口约定 V1

更新时间：2026-08-08

## 开发地址

- 后端：`http://127.0.0.1:8000`
- Swagger：`http://127.0.0.1:8000/docs`
- 前端：`http://127.0.0.1:5173`
- API 前缀：`/api/v1`

## 核心接口

### 智能分析

`POST /api/v1/analysis/query`

```json
{
  "question": "统计最近7天各产线产量趋势"
}
```

响应必须稳定包含：`task_id`、`conversation_id`、`question`、`intent`、`plan`、`columns`、`rows`、`conclusion`、`steps`。`sql`和`chart`允许为空。

### 数据集

- `GET /api/v1/datasets/status`：检查 CSV 目录。
- `GET /api/v1/datasets`：列出数据集。
- `GET /api/v1/datasets/{name}`：查看字段和样例。
- `GET /api/v1/datasets/{name}/rows`：分页预览。

### 历史记录

- `GET /api/v1/history/tasks`
- `GET /api/v1/history/tasks/{task_id}`
- `DELETE /api/v1/history/tasks/{task_id}`

## 联调约定

- 日期统一使用 `YYYY-MM-DD`，时间戳使用 ISO 8601。
- 分析表格统一使用 `columns + rows`。
- 图表统一使用 `type + title + option`。
- 前端不得保存 DeepSeek API Key。
- 后端错误必须返回明确状态码和错误说明。
- 后端无法连接时，前端可回退 Mock，但页面必须明显提示。

