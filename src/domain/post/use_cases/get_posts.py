from typing import List, Tuple, Sequence

from src.db.db import database
from src.db.models.posts import Post
from src.db.repositories.posts import PostRepository


class GetPostsUseCase:
    def __init__(self):
        pass

    async def execute(self, page: int = 1, size: int = 10) -> Tuple[Sequence[Post], int]:
        skip = (page - 1) * size
        async with database.session() as session:
            self.repository = PostRepository(session)
            return await self.repository.get_all_paginated(skip=skip, limit=size)
