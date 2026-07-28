from typing import Any

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.knowledge.model import AnalysisTopic, BusinessMetric, BusinessObject, BusinessRule


class BaseKnowledgeRepository:
    model: Any
    code_field: str
    name_field: str

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self, keyword: str | None = None, category: str | None = None, status: str | None = "active") -> list[Any]:
        query = select(self.model)
        if keyword:
            pattern = f"%{keyword}%"
            query = query.where(or_(
                getattr(self.model, self.code_field).ilike(pattern),
                getattr(self.model, self.name_field).ilike(pattern),
                self.model.description.ilike(pattern),
            ))
        if category and hasattr(self.model, "category"):
            query = query.where(self.model.category == category)
        if status:
            query = query.where(self.model.status == status)
        return list(await self.session.scalars(query.order_by(getattr(self.model, self.name_field))))

    async def get_by_code(self, code: str) -> Any | None:
        return await self.session.scalar(select(self.model).where(getattr(self.model, self.code_field) == code))

    async def create(self, values: dict[str, Any]) -> Any:
        entity = self.model(**values)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: Any, values: dict[str, Any]) -> Any:
        for key, value in values.items():
            setattr(entity, key, value)
        if isinstance(entity, BusinessMetric):
            entity.version += 1
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: Any) -> None:
        await self.session.execute(delete(self.model).where(self.model.id == entity.id))
        await self.session.commit()


class ObjectRepository(BaseKnowledgeRepository):
    model = BusinessObject
    code_field = "object_code"
    name_field = "object_name"


class MetricRepository(BaseKnowledgeRepository):
    model = BusinessMetric
    code_field = "metric_code"
    name_field = "metric_name"


class RuleRepository(BaseKnowledgeRepository):
    model = BusinessRule
    code_field = "rule_code"
    name_field = "rule_name"


class TopicRepository(BaseKnowledgeRepository):
    model = AnalysisTopic
    code_field = "topic_code"
    name_field = "topic_name"
