from sqlalchemy.ext.asyncio import AsyncSession

from models.comments import Comment
from repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Comment, session)
