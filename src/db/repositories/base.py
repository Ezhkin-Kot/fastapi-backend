from typing import Any, Generic, Sequence, Tuple, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, obj_id: Any) -> T | None:
        return await self.session.get(self.model, obj_id)

    async def get_all_paginated(
        self, skip: int = 0, limit: int = 10
    ) -> Tuple[Sequence[T], int]:
        query = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = result.scalars().all()

        count_query = select(func.count(self.model.id))
        total_count_result = await self.session.execute(count_query)
        total = total_count_result.scalar_one()

        return items, total

    async def get_all(self) -> Sequence[T]:
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, data: dict) -> T:
        db_obj = self.model(**data)
        self.session.add(db_obj)
        return db_obj

    async def update(self, db_obj: T, update_data: dict) -> T:
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        self.session.add(db_obj)
        return db_obj

    async def delete(self, db_obj: T) -> None:
        await self.session.delete(db_obj)
