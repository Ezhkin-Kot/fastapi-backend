import uuid
from src.db.db import database
from src.db.models.posts import Post
from src.db.repositories.posts import PostRepository


class GetPostUseCase:
    def __init__(self):
        pass

    async def execute(self, post_id: uuid.UUID) -> Post | None:
        async with database.session() as session:
            self.repository = PostRepository(session)
            return await self.repository.get(post_id)
