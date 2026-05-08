from sqlalchemy.ext.asyncio import AsyncSession

from src.models.posts import Post
from src.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    def __init__(self, session: AsyncSession):
        super().__init__(Post, session)
