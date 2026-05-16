import uuid
from src.db.db import database
from src.db.repositories.posts import PostRepository


class DeletePostUseCase:
    def __init__(self):
        pass

    async def execute(self, post_id: uuid.UUID) -> bool:
        async with database.session() as session:
            self.repository = PostRepository(session)
            post = await self.repository.get(post_id)
            if not post:
                return False
            await self.repository.delete(post)
            return True
