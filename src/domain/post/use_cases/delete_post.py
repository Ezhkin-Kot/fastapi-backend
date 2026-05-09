import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.posts import PostRepository


class DeletePostUseCase:
    def __init__(self, session: AsyncSession):
        self.repository = PostRepository(session)

    async def execute(self, post_id: uuid.UUID) -> bool:
        post = await self.repository.get(post_id)
        if not post:
            return False
        await self.repository.delete(post)
        return True
