from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import settings
from app.modules.sql_execution.repository import SQLExecutionRepository
from app.modules.sql_execution.schemas import (
    SQLExecuteRequest,
    SQLExecutionRead,
    SQLValidateRequest,
    SQLValidateResponse,
)
from app.modules.sql_execution.service import SQLExecutionService

router = APIRouter()


def get_service() -> SQLExecutionService:
    return SQLExecutionService(
        SQLExecutionRepository(settings.resolved_data_dir),
        max_rows=settings.sql_max_rows,
        allowed_schemas=set(settings.business_schemas),
    )


Service = Annotated[SQLExecutionService, Depends(get_service)]


@router.post("/validate", response_model=SQLValidateResponse)
async def validate_sql(payload: SQLValidateRequest, service: Service) -> SQLValidateResponse:
    return service.validate(payload.sql)


@router.post("/execute", response_model=SQLExecutionRead)
async def execute_sql(payload: SQLExecuteRequest, service: Service) -> SQLExecutionRead:
    return await service.execute(payload.sql, payload.parameters)


@router.get("/executions", response_model=list[SQLExecutionRead])
async def list_executions(service: Service, limit: int = Query(default=50, ge=1, le=200)) -> list[SQLExecutionRead]:
    return [SQLExecutionRead.model_validate(item) for item in service.repository.list(limit)]


@router.get("/executions/{execution_id}", response_model=SQLExecutionRead)
async def get_execution(execution_id: UUID, service: Service) -> SQLExecutionRead:
    item = service.repository.get(str(execution_id))
    if not item:
        raise HTTPException(status_code=404, detail="SQL执行记录不存在")
    return SQLExecutionRead.model_validate(item)
