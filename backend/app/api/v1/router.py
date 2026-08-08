from fastapi import APIRouter

from app.modules.analysis.router import router as analysis_router
from app.modules.analytics.router import router as analytics_router
from app.modules.datasets.router import router as datasets_router
from app.modules.history.router import router as history_router
from app.modules.knowledge.router import router as knowledge_router
from app.modules.metadata.router import router as metadata_router
from app.modules.modeling.router import router as modeling_router
from app.modules.reporting.router import router as reporting_router
from app.modules.sql_execution.router import router as sql_router
from app.modules.system.router import router as catalog_router
from app.modules.visualization.router import router as visualization_router

api_router = APIRouter()
api_router.include_router(analysis_router, prefix="/analysis", tags=["analysis"])
api_router.include_router(catalog_router, prefix="/catalog", tags=["catalog"])
api_router.include_router(knowledge_router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(metadata_router, prefix="/metadata", tags=["metadata"])
api_router.include_router(modeling_router, prefix="/modeling", tags=["modeling"])
api_router.include_router(sql_router, prefix="/sql", tags=["sql"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(datasets_router, prefix="/datasets", tags=["datasets"])
api_router.include_router(visualization_router, prefix="/visualization", tags=["visualization"])
api_router.include_router(history_router, prefix="/history", tags=["history"])
api_router.include_router(reporting_router, prefix="/reports", tags=["reports"])
