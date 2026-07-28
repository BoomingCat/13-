from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.modules.analytics.schemas import (
    AnalysisRowsResponse,
    AnomalyRequest,
    RankingRequest,
    SummaryRequest,
    SummaryResponse,
)
from app.modules.analytics.service import AnalyticsService

router = APIRouter()


def get_service() -> AnalyticsService:
    return AnalyticsService()


Service = Annotated[AnalyticsService, Depends(get_service)]


@router.post("/summary", response_model=SummaryResponse)
async def summarize(payload: SummaryRequest, service: Service) -> SummaryResponse:
    try:
        return service.summarize(payload.columns, payload.rows, payload.numeric_columns)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post("/ranking", response_model=AnalysisRowsResponse)
async def ranking(payload: RankingRequest, service: Service) -> AnalysisRowsResponse:
    try:
        return service.rank(
            payload.columns,
            payload.rows,
            payload.category_column,
            payload.value_column,
            payload.order == "desc",
            payload.limit,
        )
    except (ValueError, IndexError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post("/anomalies", response_model=AnalysisRowsResponse)
async def anomalies(payload: AnomalyRequest, service: Service) -> AnalysisRowsResponse:
    try:
        return service.anomalies(
            payload.columns,
            payload.rows,
            payload.value_column,
            payload.threshold,
        )
    except (ValueError, IndexError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
