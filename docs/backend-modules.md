# 后端模块说明

后端采用“按业务能力聚合”的模块化结构。每个业务模块自行管理路由、请求模型、服务、数据库模型和 Repository，避免在多个横向目录之间来回查找。

```text
backend/app/
├─ main.py
├─ api/v1/
│  └─ router.py                 # 只负责汇总各模块路由
├─ core/
│  └─ config.py                 # 环境变量和全局配置
├─ infrastructure/
│  ├─ database/                 # SQLAlchemy引擎和会话
│  ├─ llm/                      # DeepSeek适配器，默认关闭
│  └─ sql/                      # SQL安全检查与只读执行
└─ modules/
   ├─ analysis/                 # 智能问析闭环
   │  ├─ router.py
   │  ├─ schemas.py
   │  ├─ model.py
   │  ├─ repository.py
   │  ├─ planner.py
   │  ├─ templates.py
   │  ├─ service.py
   │  └─ state.py
   ├─ knowledge/                # 业务指标和规则
   │  ├─ router.py
   │  ├─ schemas.py
   │  ├─ model.py
   │  ├─ repository.py
   │  └─ service.py
   ├─ metadata/                 # 表、字段和关系理解
   │  ├─ router.py
   │  ├─ schemas.py
   │  ├─ model.py
   │  ├─ repository.py
   │  ├─ scanner.py
   │  └─ service.py
   ├─ modeling/                 # 六类受控机器学习算法
   │  ├─ router.py
   │  ├─ schemas.py
   │  └─ service.py
   ├─ reporting/                # 分析报告
   │  └─ service.py
   └─ system/                   # 健康状态和运行配置
      └─ router.py
```

## 模块依赖方向

```text
API汇总层
→ 业务模块
→ infrastructure
→ PostgreSQL / DeepSeek
```

业务模块之间尽量不直接访问对方数据库表；确需复用时通过对应服务接口调用。

## 新功能放置规则

- 新分析场景：`modules/analysis/`
- 新业务指标或规则：`modules/knowledge/`
- 数据源扫描、血缘或图谱：`modules/metadata/`
- 新算法：`modules/modeling/`
- PDF、Excel导出：`modules/reporting/`
- DeepSeek协议与鉴权：`infrastructure/llm/`
- SQL限制、超时和执行：`infrastructure/sql/`
- 数据库连接池：`infrastructure/database/`

