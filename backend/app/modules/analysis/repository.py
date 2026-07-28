from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analysis.model import AnalysisTask


class AnalysisRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, task: AnalysisTask) -> AnalysisTask:
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def list_recent(self, limit: int = 50) -> list[AnalysisTask]:
        query = select(AnalysisTask).order_by(AnalysisTask.created_at.desc()).limit(limit)
        return list(await self.session.scalars(query))

    async def get(self, task_id: UUID) -> AnalysisTask | None:
        return await self.session.get(AnalysisTask, task_id)
