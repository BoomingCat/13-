from app.infrastructure.llm.base import ChatMessage, ChatResult


class DisabledLLMClient:
    async def chat(self, messages: list[ChatMessage], *, temperature: float = 0.1) -> ChatResult:
        del messages, temperature
        raise RuntimeError("大模型调用尚未启用。请设置 LLM_ENABLED=true 并配置 LLM_API_KEY。")
