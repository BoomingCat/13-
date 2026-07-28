from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.modules.knowledge.router import get_service
from app.modules.knowledge.schemas import MetricRead
from app.modules.knowledge.service import KnowledgeService
from app.modules.metadata.json_repository import JsonMetadataRepository
from app.modules.metadata.service import MetadataService

router = APIRouter()


@router.get("/metrics")
async def metrics(
    service: Annotated[KnowledgeService, Depends(get_service)],
) -> dict[str, list[dict]]:
    items = [
        MetricRead.model_validate(item)
        for item in await service.metrics.list()
    ]
    return {"items": [
        {
            "code": metric.metric_code,
            "name": metric.metric_name,
            "description": metric.description,
            "formula": metric.formula_expression,
            "source_tables": metric.source_tables,
            "synonyms": metric.synonyms,
        }
        for metric in items
    ]}


@router.get("/tables")
async def tables() -> dict[str, list[dict]]:
    items = MetadataService(JsonMetadataRepository(settings.resolved_data_dir)).list_tables()
    return {"items": [item.model_dump() for item in items]}


@router.get("/runtime")
async def runtime() -> dict[str, str | bool]:
    return {
        "storage_backend": settings.storage_backend,
        "query_executor": settings.query_executor,
        "database_schema": settings.database_schema,
        "llm_enabled": settings.llm_enabled,
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
    }
