# DataMind Agent

面向制造企业数据底座的智能问析 Agent 基础框架。

## 当前包含

- Vue 3 + TypeScript 多页面工作台
- 本地规则式智能问析：生产、质量、设备、库存四类场景
- 业务指标的新增、编辑、删除、搜索及浏览器持久化
- 数据表、字段、类型、业务说明和数据量展示
- 分析执行轨迹、结果表格、ECharts 图表和 SQL 展示
- 本地分析历史记录及清空功能
- FastAPI 后端及版本化 API
- 不调用 Agent API 的前端本地 Mock 分析闭环
- 可替换的后端 Agent 接口（当前默认不调用）
- DeepSeek API 适配器（默认禁用，不会发起请求）
- 规则式任务规划器、指标目录、元数据目录和 SQL 安全校验
- PostgreSQL + pgvector 初始化表结构
- Redis、MinIO、Nginx 与 Docker Compose
- 健康检查、问析接口与基础测试

## 目录

```text
backend/       FastAPI、Agent、业务服务、测试
frontend/      Vue 3 前端
database/      数据库初始化及演示数据
deploy/        Nginx 等部署配置
docs/          架构与后续设计文档
```

## Docker 启动

1. 将 `.env.example` 复制为 `.env`，修改密码。
2. 启动：`docker compose up --build`
3. 前端：http://localhost:5173
4. API 文档：http://localhost:8000/docs
5. MinIO 控制台：http://localhost:9001

默认由前端读取本地模拟数据，不会请求 Agent、后端或大模型 API，无需模型密钥即可演示基本链路。

后端 `/api/v1/analysis/query`、`/api/v1/catalog/metrics`、`/api/v1/catalog/tables` 等接口均保留；当前前端尚未连接这些接口。

如需只演示前端，可进入 `frontend` 安装依赖后运行 `npm run dev`；FastAPI、PostgreSQL、Redis 和 MinIO 均不是当前演示的必需项。

DeepSeek 的预留接入方式见 `docs/deepseek-integration.md`。在主动设置 `LLM_ENABLED=true` 之前，系统不会调用模型。

后端模块划分、接口及扩展顺序见 `docs/backend-modules.md`。

## 本地开发

后端：

```bash
cd backend
python -m venv .venv
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

当前后端默认使用以下离线开发配置：

```env
STORAGE_BACKEND=json
QUERY_EXECUTOR=mock
LLM_ENABLED=false
```

业务知识保存在 `backend/data/knowledge/`。知识管理、指标目录和规则式问析均可在不启动数据库、不配置 DeepSeek 密钥的情况下运行；Mock 查询仍会通过真实 SQL 安全校验。

当前离线后端已提供：

- 业务知识管理：对象、指标、规则、分析主题及统一搜索
- 数据资源理解：数据源、数据表、字段、样例值、主外键关系和元数据搜索
- 智能问析：规则规划、指标/表匹配、受控 SQL、Mock 执行、结论和图表
- SQL业务接口：安全校验、执行、拒绝记录和审计查询
- 统计分析：摘要、排名和 Z-Score 异常检测
- 可视化：表格、指标卡、折线图、柱状图、饼图和散点图协议
- 机器学习：六种算法、训练测试集划分、评估和特征重要性
- 历史与报告：问析历史、SQL历史和 Markdown 报告

验证后端：

```bash
cd backend
pytest -q
```

前端：

```bash
cd frontend
npm install
npm run dev
```

## 下一步

1. 完成 JSON 元数据目录以及数据表、字段、关系检索接口。
2. 扩展规则规划器，形成指标、维度、时间范围和数据表组成的分析计划。
3. 增加表字段白名单、查询超时和 SQL 执行审计。
4. 完善 Scikit-learn 训练、评估、保存和推理流程。
5. 后期切换 OpenGauss Repository，并完成 DeepSeek 联调。
