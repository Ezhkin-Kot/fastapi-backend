import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.comments import CommentCreate
from src.db.models.comments import Comment
from src.db.models.users import User
from src.db.repositories.comments import CommentRepository


class CreateCommentUseCase:
    def __init__(self, session: AsyncSession):
        self.repository = CommentRepository(session)

    async def execute(
        self, post_id: uuid.UUID, comment_in: CommentCreate, author: User
    ) -> Comment:
        comment_data = comment_in.model_dump()
        comment_data["author_id"] = author.id
        comment_data["post_id"] = post_id
        new_comment = await self.repository.create(comment_data)
        return new_comment
