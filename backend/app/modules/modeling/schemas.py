from typing import Literal

from pydantic import BaseModel, Field

Algorithm = Literal["linear_regression", "logistic_regression", "decision_tree", "random_forest", "kmeans", "isolation_forest"]


class ModelRunRequest(BaseModel):
    algorithm: Algorithm
    features: list[list[float]] = Field(min_length=2)
    target: list[float] | None = None
    feature_names: list[str] = Field(default_factory=list)
    test_size: float = Field(default=0.2, ge=0.1, le=0.5)
    parameters: dict[str, float | int | str | bool] = Field(default_factory=dict)


class ModelRunResponse(BaseModel):
    algorithm: Algorithm
    sample_count: int
    metrics: dict[str, float]
    predictions: list[float | int]
    train_count: int = 0
    test_count: int = 0
    feature_importance: dict[str, float] = Field(default_factory=dict)
    explanation: str
