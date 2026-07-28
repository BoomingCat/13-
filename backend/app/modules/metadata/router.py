from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import settings
from app.modules.metadata.json_repository import JsonMetadataRepository
from app.modules.metadata.schemas import (
    DataSourceRead,
    MetadataSearchResult,
    RelationRead,
    TableRead,
)
from app.modules.metadata.service import MetadataNotFoundError, MetadataService

router = APIRouter()


def get_service() -> MetadataService:
    return MetadataService(JsonMetadataRepository(settings.resolved_data_dir))


Service = Annotated[MetadataService, Depends(get_service)]


@router.get("/sources", response_model=list[DataSourceRead])
async def list_sources(service: Service) -> list[DataSourceRead]:
    return service.repository.list_sources()


@router.post("/sources/{source_id}/test")
async def test_source(source_id: str, service: Service) -> dict[str, str | bool]:
    source = next((item for item in service.repository.list_sources() if item.id == source_id), None)
    if not source:
        raise HTTPException(status_code=404, detail=f"数据源 {source_id} 不存在")
    return {
        "success": settings.storage_backend == "database",
        "mode": settings.storage_backend,
        "message": "当前为离线元数据模式，未发起真实数据库连接。",
    }


@router.get("/tables", response_model=list[TableRead])
@router.get("/scan", response_model=list[TableRead])
async def list_tables(service: Service) -> list[TableRead]:
    return service.list_tables()


@router.get("/tables/{table_name}", response_model=TableRead)
async def get_table(table_name: str, service: Service) -> TableRead:
    try:
        return service.get_table(table_name)
    except MetadataNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/relations", response_model=list[RelationRead])
async def list_relations(service: Service) -> list[RelationRead]:
    return service.repository.list_relations()


@router.get("/search", response_model=MetadataSearchResult)
async def search_metadata(service: Service, q: str = Query(min_length=1)) -> MetadataSearchResult:
    return service.search(q)
