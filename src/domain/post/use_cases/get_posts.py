from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.posts import Post
from src.db.repositories.posts import PostRepository


class GetPostsUseCase:
    def __init__(self, session: AsyncSession):
        self.repository = PostRepository(session)

    async def execute(self) -> List[Post]:
        return await self.repository.get_all()
