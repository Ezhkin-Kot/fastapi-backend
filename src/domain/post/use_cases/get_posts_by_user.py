import uuid
from typing import Sequence

from src.db.db import database
from src.db.models.posts import Post
from src.db.repositories.posts import PostRepository


class GetPostsByUserUseCase:
    def __init__(self):
        pass

    async def execute(
        self, user_id: uuid.UUID, page: int = 1, size: int = 10
    ) -> (Sequence[Post], int):
        skip = (page - 1) * size
        async with database.session() as session:
            repo = PostRepository(session)
            return await repo.get_by_user_id_paginated(
                user_id=user_id, skip=skip, limit=size
            )
