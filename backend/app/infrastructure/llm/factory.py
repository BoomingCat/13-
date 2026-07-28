from app.core.config import Settings, settings
from app.infrastructure.llm.base import LLMClient
from app.infrastructure.llm.deepseek import DeepSeekClient
from app.infrastructure.llm.disabled import DisabledLLMClient


def build_llm_client(config: Settings = settings) -> LLMClient:
    if not config.llm_enabled:
        return DisabledLLMClient()
    if config.llm_provider != "deepseek":
        raise ValueError(f"暂不支持的 LLM_PROVIDER: {config.llm_provider}")
    return DeepSeekClient(
        api_key=config.llm_api_key,
        base_url=config.llm_base_url,
        model=config.llm_model,
        timeout_seconds=config.llm_timeout_seconds,
        max_retries=config.llm_max_retries,
    )
