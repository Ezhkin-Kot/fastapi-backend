import uuid
from typing import List
from src.db.db import database
from src.db.models.comments import Comment
from src.db.repositories.comments import CommentRepository


class GetCommentsUseCase:
    def __init__(self):
        pass

    async def execute(self, post_id: uuid.UUID) -> List[Comment]:
        async with database.session() as session:
            self.repository = CommentRepository(session)
            return await self.repository.get_by_post_id(post_id)
