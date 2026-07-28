from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "DataMind Agent"
    app_env: str = "development"
    app_debug: bool = True
    api_prefix: str = "/api/v1"

    storage_backend: Literal["json", "database"] = "json"
    query_executor: Literal["mock", "database"] = "mock"
    data_dir: Path = Path("data")

    database_url: str = "postgresql+asyncpg://datamind:change-me@localhost:5432/datamind"
    database_readonly_url: str = ""
    database_schema: str = "fwwb"
    business_schemas: list[str] = ["manufacturing"]

    sql_max_rows: int = 1000
    sql_timeout_seconds: int = 30

    redis_url: str = "redis://localhost:6379/0"
    minio_endpoint: str = "localhost:9000"

    llm_enabled: bool = False
    llm_provider: Literal["deepseek"] = "deepseek"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com"
    llm_model: str = "deepseek-chat"
    llm_timeout_seconds: float = 60
    llm_max_retries: int = 2

    cors_origins: list[str] = ["http://localhost:5173"]

    @property
    def backend_dir(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def resolved_data_dir(self) -> Path:
        if self.data_dir.is_absolute():
            return self.data_dir
        return self.backend_dir / self.data_dir

    @property
    def upload_dir(self) -> Path:
        return self.resolved_data_dir / "uploads"

    @property
    def model_dir(self) -> Path:
        return self.resolved_data_dir / "models"

    @property
    def report_dir(self) -> Path:
        return self.resolved_data_dir / "reports"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
