from sqlalchemy.ext.asyncio import AsyncSession

from src.models.comments import Comment
from src.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Comment, session)
