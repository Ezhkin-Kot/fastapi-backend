from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.db.models.posts import Post
from src.db.models.categories import Category
from src.db.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    def __init__(self, session: AsyncSession):
        super().__init__(Post, session)

    async def get_by_category_slug(self, slug: str) -> List[Post]:
        query = (
            select(Post)
            .join(Category)
            .where(Category.slug == slug)
            .options(joinedload(Post.author), joinedload(Post.category))
            .order_by(Post.pub_date.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
