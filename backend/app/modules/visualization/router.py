from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.modules.visualization.schemas import ChartBuildRequest, ChartResponse
from app.modules.visualization.service import VisualizationService

router = APIRouter()


def get_service() -> VisualizationService:
    return VisualizationService()


Service = Annotated[VisualizationService, Depends(get_service)]


@router.post("/recommend", response_model=ChartResponse)
@router.post("/build", response_model=ChartResponse)
async def build_chart(payload: ChartBuildRequest, service: Service) -> ChartResponse:
    try:
        return service.build(
            payload.title,
            payload.columns,
            payload.rows,
            payload.chart_type,
            payload.category_column,
            payload.value_columns,
        )
    except (ValueError, IndexError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
