from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app.core.config import settings
from app.modules.history.repository import AnalysisHistoryRepository
from app.modules.history.schemas import AnalysisHistoryRead
from app.modules.history.service import HistoryService

router = APIRouter()


def get_service() -> HistoryService:
    return HistoryService(AnalysisHistoryRepository(settings.resolved_data_dir))


Service = Annotated[HistoryService, Depends(get_service)]


@router.get("/tasks", response_model=list[AnalysisHistoryRead])
async def list_tasks(service: Service, limit: int = Query(default=50, ge=1, le=200)) -> list[AnalysisHistoryRead]:
    return service.list(limit)


@router.get("/tasks/{task_id}", response_model=AnalysisHistoryRead)
async def get_task(task_id: UUID, service: Service) -> AnalysisHistoryRead:
    item = service.get(str(task_id))
    if not item:
        raise HTTPException(status_code=404, detail="问析任务不存在")
    return item


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: UUID, service: Service) -> Response:
    if not service.repository.delete(str(task_id)):
        raise HTTPException(status_code=404, detail="问析任务不存在")
    return Response(status_code=204)
