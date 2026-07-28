# 第一模块：业务知识管理

## 模块目标

围绕制造业场景维护 Agent 分析所需的业务对象、业务指标、业务规则和分析主题，确保后续自然语言分析使用统一、可追踪的业务口径。

## 数据表

```text
fwwb.business_objects
fwwb.business_metrics
fwwb.business_rules
fwwb.analysis_topics
```

初始化脚本：

```text
database/fwwb/002_business_knowledge.sql
```

## 接口

```text
GET    /api/v1/knowledge/search?q=良率

GET    /api/v1/knowledge/objects
POST   /api/v1/knowledge/objects
PUT    /api/v1/knowledge/objects/{code}
DELETE /api/v1/knowledge/objects/{code}

GET    /api/v1/knowledge/metrics
POST   /api/v1/knowledge/metrics
PUT    /api/v1/knowledge/metrics/{code}
DELETE /api/v1/knowledge/metrics/{code}

GET    /api/v1/knowledge/rules
POST   /api/v1/knowledge/rules
PUT    /api/v1/knowledge/rules/{code}
DELETE /api/v1/knowledge/rules/{code}

GET    /api/v1/knowledge/topics
POST   /api/v1/knowledge/topics
PUT    /api/v1/knowledge/topics/{code}
DELETE /api/v1/knowledge/topics/{code}
```

列表接口支持：

```text
keyword     名称、编码和说明模糊查询
category    生产、质量、设备、库存分类过滤
item_status active/inactive状态过滤
```

## 初始制造业知识

- 7个业务对象
- 5个业务指标
- 4条业务规则
- 4个分析主题

其中包括产量、工序良率、不良率、设备停机时长和安全库存缺口等核心指标。

## 验收标准

1. 四张表存在于 `fwwb` Schema。
2. 初始化数据数量分别为7、5、4、4。
3. CRUD接口正常返回。
4. 指标更新后版本号自动递增。
5. 搜索“良率”能够返回相关指标、规则和分析主题。
6. 五个 `*_fwwb` 账号能够访问知识表。
