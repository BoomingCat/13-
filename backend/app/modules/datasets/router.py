from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import settings
from app.modules.datasets.repository import (
    CsvDatasetRepository,
    DatasetConfigurationError,
    DatasetNotFoundError,
)
from app.modules.datasets.schemas import (
    DatasetDetail,
    DatasetRows,
    DatasetStatus,
    DatasetSummary,
)

router = APIRouter()


def get_repository() -> CsvDatasetRepository:
    return CsvDatasetRepository(settings.resolved_external_data_dir)


Repository = Annotated[CsvDatasetRepository, Depends(get_repository)]


def _http_error(error: Exception) -> HTTPException:
    if isinstance(error, DatasetNotFoundError):
        return HTTPException(status_code=404, detail=str(error))
    return HTTPException(status_code=503, detail=str(error))


@router.get("/status", response_model=DatasetStatus, summary="查看CSV数据目录状态")
async def status(repository: Repository) -> DatasetStatus:
    return repository.status()


@router.get("", response_model=list[DatasetSummary], summary="列出全部CSV数据集")
async def list_datasets(repository: Repository) -> list[DatasetSummary]:
    try:
        return repository.list()
    except DatasetConfigurationError as error:
        raise _http_error(error) from error


@router.get("/{name}", response_model=DatasetDetail, summary="查看数据集字段和样例值")
async def dataset_detail(name: str, repository: Repository) -> DatasetDetail:
    try:
        return repository.detail(name)
    except (DatasetConfigurationError, DatasetNotFoundError) as error:
        raise _http_error(error) from error


@router.get("/{name}/rows", response_model=DatasetRows, summary="分页预览数据集")
async def dataset_rows(
    name: str,
    repository: Repository,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> DatasetRows:
    try:
        return repository.rows(name, offset, limit)
    except (DatasetConfigurationError, DatasetNotFoundError) as error:
        raise _http_error(error) from error
