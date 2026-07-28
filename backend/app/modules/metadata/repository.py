from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.metadata.model import MetadataTable


class MetadataRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_tables(self) -> list[MetadataTable]:
        result = await self.session.scalars(select(MetadataTable).options(selectinload(MetadataTable.columns)).order_by(MetadataTable.schema_name, MetadataTable.table_name))
        return list(result.unique())

