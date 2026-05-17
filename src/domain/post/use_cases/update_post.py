import uuid
from src.db.db import database
from src.schemas.posts import PostUpdate
from src.db.models.posts import Post
from src.db.repositories.posts import PostRepository


class UpdatePostUseCase:
    def __init__(self):
        pass

    async def execute(self, post_id: uuid.UUID, post_update: PostUpdate) -> Post | None:
        async with database.session() as session:
            self.repository = PostRepository(session)
            post = await self.repository.get(post_id)
            if not post:
                return None
            update_data = post_update.model_dump(exclude_unset=True)
            updated_post = await self.repository.update(post, update_data)
            await session.flush()
            await session.refresh(updated_post, attribute_names=["comments"])
            return updated_post
