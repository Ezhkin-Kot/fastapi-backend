import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.comments import Comment
from src.repositories.comments import CommentRepository


class GetCommentsUseCase:
    def __init__(self, session: AsyncSession):
        self.repository = CommentRepository(session)

    async def execute(self, post_id: uuid.UUID) -> List[Comment]:
        query = select(Comment).where(Comment.post_id == post_id)
        result = await self.repository.session.execute(query)
        return result.scalars().all()
