import uuid

from src.db.db import database
from src.db.models.users import User
from src.db.models.comments import Comment
from src.db.repositories.comments import CommentRepository
from src.schemas.comments import CommentUpdate
from src.core.exceptions import ForbiddenError, NotFoundError


class UpdateCommentUseCase:
    def __init__(self):
        pass

    async def execute(
        self, comment_id: uuid.UUID, comment_update: CommentUpdate, current_user: User
    ) -> Comment:
        async with database.session() as session:
            repo = CommentRepository(session)
            comment = await repo.get(comment_id)
            if not comment:
                raise NotFoundError(message="Comment not found")

            if comment.author_id != current_user.id:
                raise ForbiddenError(message="You can only edit your own comments")

            update_data = comment_update.model_dump(exclude_unset=True)
            updated_comment = await repo.update(comment, update_data)
            return updated_comment
