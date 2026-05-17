import uuid

from fastapi import APIRouter, Depends, status

from src.api.dependencies import update_comment_use_case, delete_comment_use_case
from src.domain.comment.use_cases.update_comment import UpdateCommentUseCase
from src.domain.comment.use_cases.delete_comment import DeleteCommentUseCase
from src.db.models.users import User
from src.schemas.comments import CommentUpdate, CommentResponse
from src.services.auth import get_current_user

router = APIRouter()


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
)
async def update_comment(
    comment_id: uuid.UUID,
    comment_update: CommentUpdate,
    use_case: UpdateCommentUseCase = Depends(update_comment_use_case),
    current_user: User = Depends(get_current_user),
):
    updated_comment = await use_case.execute(comment_id, comment_update, current_user)
    return CommentResponse.model_validate(updated_comment)


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    comment_id: uuid.UUID,
    use_case: DeleteCommentUseCase = Depends(delete_comment_use_case),
    current_user: User = Depends(get_current_user),
):
    await use_case.execute(comment_id, current_user)
    return
