import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.comments import Comment
from src.db.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Comment, session)

    async def get_by_post_id(self, post_id: uuid.UUID) -> List[Comment]:
        query = select(Comment).where(Comment.post_id == post_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
