import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.posts import PostUpdate
from src.models.posts import Post
from src.repositories.posts import PostRepository


class UpdatePostUseCase:
    def __init__(self, session: AsyncSession):
        self.repository = PostRepository(session)

    async def execute(self, post_id: uuid.UUID, post_update: PostUpdate) -> Post | None:
        post = await self.repository.get(post_id)
        if not post:
            return None
        update_data = post_update.model_dump(exclude_unset=True)
        return await self.repository.update(post, update_data)
