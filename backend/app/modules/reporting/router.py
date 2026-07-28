from fastapi import APIRouter

from app.modules.reporting.schemas import ReportBuildRequest, ReportBuildResponse
from app.modules.reporting.service import ReportService

router = APIRouter()


@router.post("", response_model=ReportBuildResponse)
async def build_report(payload: ReportBuildRequest) -> ReportBuildResponse:
    content = ReportService().build_markdown(
        question=payload.question,
        sql=payload.sql,
        columns=payload.columns,
        rows=payload.rows,
        conclusion=payload.conclusion,
    )
    return ReportBuildResponse(content=content)
