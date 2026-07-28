from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.infrastructure.database import get_db
from app.infrastructure.sql.executor import MockQueryExecutor, ReadOnlyQueryExecutor
from app.modules.analysis.schemas import AnalysisRequest, AnalysisResponse
from app.modules.analysis.service import AgentService
from app.modules.history.repository import AnalysisHistoryRepository
from app.modules.history.service import HistoryService

router = APIRouter()


async def get_agent_service() -> AsyncIterator[AgentService]:
    if settings.query_executor == "mock":
        yield AgentService(MockQueryExecutor(
            max_rows=settings.sql_max_rows,
            allowed_schemas=set(settings.business_schemas),
        ))
        return
    if settings.query_executor != "database":
        raise RuntimeError(f"不支持的 QUERY_EXECUTOR: {settings.query_executor}")
    async for session in get_db():
        yield AgentService(ReadOnlyQueryExecutor(
            session,
            max_rows=settings.sql_max_rows,
            allowed_schemas=set(settings.business_schemas),
        ))


@router.post("/query", response_model=AnalysisResponse)
async def analyze(
    payload: AnalysisRequest,
    service: Annotated[AgentService, Depends(get_agent_service)],
) -> AnalysisResponse:
    response = await service.analyze(payload)
    HistoryService(AnalysisHistoryRepository(settings.resolved_data_dir)).save_analysis(
        response.model_dump(mode="json")
    )
    return response


@router.get("/examples")
async def examples() -> dict[str, list[str]]:
    return {
        "examples": [
            "统计每条产线最近7天的产量趋势",
            "分析各工序本月良率",
            "找出最近一个月不良数量最高的产品",
            "分析设备停机时间和产品不良率是否相关",
            "使用 Isolation Forest 检测异常生产记录",
        ]
    }
