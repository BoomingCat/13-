from typing import Any

from app.modules.history.repository import AnalysisHistoryRepository
from app.modules.history.schemas import AnalysisHistoryRead


class HistoryService:
    def __init__(self, repository: AnalysisHistoryRepository) -> None:
        self.repository = repository

    def save_analysis(self, result: dict[str, Any]) -> AnalysisHistoryRead:
        return AnalysisHistoryRead.model_validate(self.repository.save(result))

    def list(self, limit: int) -> list[AnalysisHistoryRead]:
        return [AnalysisHistoryRead.model_validate(item) for item in self.repository.list(limit)]

    def get(self, task_id: str) -> AnalysisHistoryRead | None:
        item = self.repository.get(task_id)
        return AnalysisHistoryRead.model_validate(item) if item else None
