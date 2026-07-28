from fastapi import APIRouter, HTTPException

from app.modules.modeling.schemas import ModelRunRequest, ModelRunResponse
from app.modules.modeling.service import ModelRunner

router = APIRouter()


@router.get("/algorithms")
async def algorithms() -> dict[str, list[str]]:
    return {"items": ["linear_regression", "logistic_regression", "decision_tree", "random_forest", "kmeans", "isolation_forest"]}


@router.post("/run", response_model=ModelRunResponse)
async def run_model(payload: ModelRunRequest) -> ModelRunResponse:
    try:
        return ModelRunner().run(payload)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
