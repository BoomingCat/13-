from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.knowledge.json_repository import build_json_repositories
from app.modules.knowledge.model import (
    AnalysisTopic,
    BusinessMetric,
    BusinessObject,
    BusinessRule,
)
from app.modules.knowledge.repository import (
    MetricRepository,
    ObjectRepository,
    RuleRepository,
    TopicRepository,
)
from app.modules.knowledge.schemas import (
    KnowledgeSearchResult,
    MetricRead,
    ObjectRead,
    RuleRead,
    TopicRead,
)


class KnowledgeConflictError(Exception):
    pass


class KnowledgeNotFoundError(Exception):
    pass


class KnowledgeService:
    def __init__(self, objects: Any, metrics: Any, rules: Any, topics: Any) -> None:
        self.objects = objects
        self.metrics = metrics
        self.rules = rules
        self.topics = topics

    @classmethod
    def from_database(cls, session: AsyncSession) -> "KnowledgeService":
        return cls(
            ObjectRepository(session),
            MetricRepository(session),
            RuleRepository(session),
            TopicRepository(session),
        )

    @classmethod
    def from_json(cls) -> "KnowledgeService":
        return cls(*build_json_repositories(settings.resolved_data_dir))

    async def create_unique(self, repository: Any, code: str, values: dict[str, Any]) -> Any:
        if await repository.get_by_code(code):
            raise KnowledgeConflictError(f"编码 {code} 已存在")
        return await repository.create(values)

    async def update_existing(self, repository: Any, code: str, values: dict[str, Any]) -> Any:
        entity = await repository.get_by_code(code)
        if not entity:
            raise KnowledgeNotFoundError(f"编码 {code} 不存在")
        return await repository.update(entity, values)

    async def delete_existing(self, repository: Any, code: str) -> None:
        entity = await repository.get_by_code(code)
        if not entity:
            raise KnowledgeNotFoundError(f"编码 {code} 不存在")
        await repository.delete(entity)

    async def search(self, query: str) -> KnowledgeSearchResult:
        # 同一个 AsyncSession 不并发执行查询，避免连接状态冲突。
        objects = await self.objects.list(keyword=query)
        metrics = await self.metrics.list(keyword=query)
        rules = await self.rules.list(keyword=query)
        topics = await self.topics.list(keyword=query)
        return KnowledgeSearchResult(
            objects=[ObjectRead.model_validate(item) for item in objects],
            metrics=[MetricRead.model_validate(item) for item in metrics],
            rules=[RuleRead.model_validate(item) for item in rules],
            topics=[TopicRead.model_validate(item) for item in topics],
        )


__all__ = [
    "AnalysisTopic", "BusinessMetric", "BusinessObject", "BusinessRule",
    "KnowledgeConflictError", "KnowledgeNotFoundError", "KnowledgeService",
]
