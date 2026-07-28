# DeepSeek 接入说明（当前不启用）

项目已提供 `backend/app/infrastructure/llm/` 适配层，默认配置：

```env
LLM_ENABLED=false
LLM_PROVIDER=deepseek
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
LLM_API_KEY=
```

`LLM_ENABLED=false` 时，工厂返回 `DisabledLLMClient`，不会创建 HTTP 客户端，也不会发起网络请求。

未来接入步骤：

1. 在 `.env` 填写 `LLM_API_KEY`。
2. 将 `LLM_ENABLED` 改为 `true`。
3. 在 Agent 规划节点中通过 `build_llm_client()` 获取客户端。
4. 向客户端传入系统提示词、业务知识、元数据和用户问题。
5. 强制模型输出结构化 JSON，再由 SQLGuard 校验 SQL。

调用示例（仅供未来接入）：

```python
from app.infrastructure.llm import build_llm_client
from app.infrastructure.llm.base import ChatMessage

client = build_llm_client()
result = await client.chat([
    ChatMessage(role="system", content="你是制造业数据分析规划器。"),
    ChatMessage(role="user", content="统计每条产线最近7天的产量趋势。"),
])
```

不要让模型直接执行 SQL。正确链路为：

```text
DeepSeek 生成计划或 SQL
→ SQLGlot 解析
→ Schema/表白名单
→ 强制 LIMIT
→ 只读数据库账号执行
→ 审计记录
```
