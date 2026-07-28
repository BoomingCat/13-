import httpx

from app.infrastructure.llm.base import ChatMessage, ChatResult


class DeepSeekClient:
    """DeepSeek OpenAI 兼容接口适配器。

    该模块只负责协议封装；只有 LLM_ENABLED=true 时工厂才会实例化它。
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        timeout_seconds: float,
        max_retries: int,
    ) -> None:
        if not api_key:
            raise ValueError("LLM_API_KEY 未配置")
        self.model = model
        self.max_retries = max_retries
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout_seconds,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )

    async def chat(self, messages: list[ChatMessage], *, temperature: float = 0.1) -> ChatResult:
        payload = {
            "model": self.model,
            "messages": [{"role": item.role, "content": item.content} for item in messages],
            "temperature": temperature,
            "stream": False,
        }
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.post("/chat/completions", json=payload)
                response.raise_for_status()
                data = response.json()
                usage = data.get("usage", {})
                return ChatResult(
                    content=data["choices"][0]["message"]["content"],
                    model=data.get("model", self.model),
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                )
            except (httpx.HTTPError, KeyError, IndexError, TypeError) as error:
                last_error = error
                if attempt == self.max_retries:
                    break
        raise RuntimeError("DeepSeek 请求失败") from last_error

    async def close(self) -> None:
        await self._client.aclose()
