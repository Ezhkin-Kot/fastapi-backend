from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.posts import Post
from src.db.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    def __init__(self, session: AsyncSession):
        super().__init__(Post, session)
