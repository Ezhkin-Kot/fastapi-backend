from typing import List
from src.db.db import database
from src.db.models.posts import Post
from src.db.repositories.posts import PostRepository


class GetPostsUseCase:
    def __init__(self):
        pass

    async def execute(self) -> List[Post]:
        async with database.session() as session:
            self.repository = PostRepository(session)
            return await self.repository.get_all()
