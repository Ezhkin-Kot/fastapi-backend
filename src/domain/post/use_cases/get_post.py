import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from models.posts import Post
from repositories.posts import PostRepository


class GetPostUseCase:
    def __init__(self, session: AsyncSession):
        self.repository = PostRepository(session)

    async def execute(self, post_id: uuid.UUID) -> Post | None:
        return await self.repository.get(post_id)
