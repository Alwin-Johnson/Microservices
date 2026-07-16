from typing import Any, Generic, Sequence, TypeVar, Type, Optional, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from shared.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: UUID | str, for_update: bool = False) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)
        if for_update:
            stmt = stmt.with_for_update()
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self) -> Sequence[ModelType]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        return db_obj

    async def update(self, id: UUID | str, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        db_obj = await self.get(id)
        if not db_obj:
            return None
            
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
            
        self.session.add(db_obj)
        await self.session.flush()
        return db_obj

    async def delete(self, id: UUID | str) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.flush()
        return result.rowcount > 0
