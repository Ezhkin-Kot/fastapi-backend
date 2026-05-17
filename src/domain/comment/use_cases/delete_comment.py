import uuid

from src.db.db import database
from src.db.models.users import User
from src.db.repositories.comments import CommentRepository
from src.core.exceptions import ForbiddenError, NotFoundError


class DeleteCommentUseCase:
    def __init__(self):
        pass

    async def execute(self, comment_id: uuid.UUID, current_user: User) -> None:
        async with database.session() as session:
            repo = CommentRepository(session)
            comment = await repo.get(comment_id)
            if not comment:
                raise NotFoundError(message="Comment not found")

            if comment.author_id != current_user.id:
                raise ForbiddenError(message="You can only delete your own comments")

            await repo.delete(comment)
