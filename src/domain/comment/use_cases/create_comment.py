import uuid
from src.db.db import database
from src.schemas.comments import CommentCreate
from src.db.models.comments import Comment
from src.db.models.users import User
from src.db.repositories.comments import CommentRepository


class CreateCommentUseCase:
    def __init__(self):
        pass

    async def execute(
        self, post_id: uuid.UUID, comment_in: CommentCreate, author: User
    ) -> Comment:
        async with database.session() as session:
            self.repository = CommentRepository(session)
            comment_data = comment_in.model_dump()
            comment_data["author_id"] = author.id
            comment_data["post_id"] = post_id
            new_comment = await self.repository.create(comment_data)
            return new_comment
