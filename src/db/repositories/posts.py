import uuid
from typing import List, Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.db.models.posts import Post
from src.db.models.categories import Category
from src.db.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    def __init__(self, session: AsyncSession):
        super().__init__(Post, session)

    async def get(self, obj_id: uuid.UUID) -> Post | None:
        query = select(Post).where(Post.id == obj_id).options(selectinload(Post.comments))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_paginated(
        self, skip: int = 0, limit: int = 10
    ) -> Tuple[Sequence[Post], int]:
        # Query for the paginated results
        query = (
            select(Post)
            .options(selectinload(Post.comments))
            .order_by(Post.pub_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        items = result.scalars().all()

        # Query for the total count
        count_query = select(func.count(Post.id))
        total_count_result = await self.session.execute(count_query)
        total = total_count_result.scalar_one()

        return items, total

    async def get_by_category_slug(
        self, slug: str, skip: int = 0, limit: int = 10
    ) -> Tuple[Sequence[Post], int]:
        base_query = select(Post).join(Category).where(Category.slug == slug)

        # Query for the paginated results
        query = (
            base_query.options(
                joinedload(Post.author),
                joinedload(Post.category),
                selectinload(Post.comments),
            )
            .order_by(Post.pub_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        items = result.scalars().all()

        # Query for the total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count_result = await self.session.execute(count_query)
        total = total_count_result.scalar_one()

        return items, total
