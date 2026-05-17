from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.categories import Category
from src.db.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession):
        super().__init__(Category, session)

    async def get_by_slug(self, slug: str) -> Category | None:
        query = select(Category).where(Category.slug == slug)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
