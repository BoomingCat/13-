from typing import Annotated, Any

from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.core.config import settings
from app.infrastructure.database import get_db
from app.modules.knowledge.schemas import (
    KnowledgeSearchResult,
    MetricCreate, MetricRead, MetricUpdate,
    ObjectCreate, ObjectRead, ObjectUpdate,
    RuleCreate, RuleRead, RuleUpdate,
    TopicCreate, TopicRead, TopicUpdate,
)
from app.modules.knowledge.service import KnowledgeConflictError, KnowledgeNotFoundError, KnowledgeService

router = APIRouter()


async def get_service() -> AsyncIterator[KnowledgeService]:
    if settings.storage_backend == "json":
        yield KnowledgeService.from_json()
        return
    if settings.storage_backend != "database":
        raise RuntimeError(f"不支持的 STORAGE_BACKEND: {settings.storage_backend}")
    async for session in get_db():
        yield KnowledgeService.from_database(session)


Service = Annotated[KnowledgeService, Depends(get_service)]


def handle_error(error: Exception) -> None:
    if isinstance(error, KnowledgeConflictError):
        raise HTTPException(status_code=409, detail=str(error)) from error
    if isinstance(error, KnowledgeNotFoundError):
        raise HTTPException(status_code=404, detail=str(error)) from error
    raise error


@router.get("/search", response_model=KnowledgeSearchResult)
async def search_knowledge(service: Service, q: str = Query(min_length=1)) -> KnowledgeSearchResult:
    return await service.search(q)


@router.get("/objects", response_model=list[ObjectRead])
async def list_objects(service: Service, keyword: str | None = None, category: str | None = None, item_status: str | None = "active") -> list[Any]:
    return await service.objects.list(keyword, category, item_status)


@router.post("/objects", response_model=ObjectRead, status_code=status.HTTP_201_CREATED)
async def create_object(payload: ObjectCreate, service: Service) -> Any:
    try:
        return await service.create_unique(service.objects, payload.object_code, payload.model_dump())
    except Exception as error:
        handle_error(error)


@router.put("/objects/{code}", response_model=ObjectRead)
async def update_object(code: str, payload: ObjectUpdate, service: Service) -> Any:
    try:
        return await service.update_existing(service.objects, code, payload.model_dump(exclude_unset=True))
    except Exception as error:
        handle_error(error)


@router.delete("/objects/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_object(code: str, service: Service) -> Response:
    try:
        await service.delete_existing(service.objects, code)
        return Response(status_code=204)
    except Exception as error:
        handle_error(error)


@router.get("/metrics", response_model=list[MetricRead])
async def list_metrics(service: Service, keyword: str | None = None, category: str | None = None, item_status: str | None = "active") -> list[Any]:
    return await service.metrics.list(keyword, category, item_status)


@router.post("/metrics", response_model=MetricRead, status_code=status.HTTP_201_CREATED)
async def create_metric(payload: MetricCreate, service: Service) -> Any:
    try:
        return await service.create_unique(service.metrics, payload.metric_code, payload.model_dump())
    except Exception as error:
        handle_error(error)


@router.put("/metrics/{code}", response_model=MetricRead)
async def update_metric(code: str, payload: MetricUpdate, service: Service) -> Any:
    try:
        return await service.update_existing(service.metrics, code, payload.model_dump(exclude_unset=True))
    except Exception as error:
        handle_error(error)


@router.delete("/metrics/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_metric(code: str, service: Service) -> Response:
    try:
        await service.delete_existing(service.metrics, code)
        return Response(status_code=204)
    except Exception as error:
        handle_error(error)


@router.get("/rules", response_model=list[RuleRead])
async def list_rules(service: Service, keyword: str | None = None, category: str | None = None, item_status: str | None = "active") -> list[Any]:
    return await service.rules.list(keyword, category, item_status)


@router.post("/rules", response_model=RuleRead, status_code=status.HTTP_201_CREATED)
async def create_rule(payload: RuleCreate, service: Service) -> Any:
    try:
        return await service.create_unique(service.rules, payload.rule_code, payload.model_dump())
    except Exception as error:
        handle_error(error)


@router.put("/rules/{code}", response_model=RuleRead)
async def update_rule(code: str, payload: RuleUpdate, service: Service) -> Any:
    try:
        return await service.update_existing(service.rules, code, payload.model_dump(exclude_unset=True))
    except Exception as error:
        handle_error(error)


@router.delete("/rules/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(code: str, service: Service) -> Response:
    try:
        await service.delete_existing(service.rules, code)
        return Response(status_code=204)
    except Exception as error:
        handle_error(error)


@router.get("/topics", response_model=list[TopicRead])
async def list_topics(service: Service, keyword: str | None = None, item_status: str | None = "active") -> list[Any]:
    return await service.topics.list(keyword, None, item_status)


@router.post("/topics", response_model=TopicRead, status_code=status.HTTP_201_CREATED)
async def create_topic(payload: TopicCreate, service: Service) -> Any:
    try:
        return await service.create_unique(service.topics, payload.topic_code, payload.model_dump())
    except Exception as error:
        handle_error(error)


@router.put("/topics/{code}", response_model=TopicRead)
async def update_topic(code: str, payload: TopicUpdate, service: Service) -> Any:
    try:
        return await service.update_existing(service.topics, code, payload.model_dump(exclude_unset=True))
    except Exception as error:
        handle_error(error)


@router.delete("/topics/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(code: str, service: Service) -> Response:
    try:
        await service.delete_existing(service.topics, code)
        return Response(status_code=204)
    except Exception as error:
        handle_error(error)
