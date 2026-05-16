import uuid
from typing import List

from fastapi import APIRouter, Depends, status

from src.schemas.comments import CommentCreate, CommentResponse
from src.api.dependencies import create_comment_use_case, get_comments_use_case
from src.domain.comment.use_cases.create_comment import CreateCommentUseCase
from src.domain.comment.use_cases.get_comments import GetCommentsUseCase
from src.db.models.users import User
from src.services.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: uuid.UUID,
    comment_in: CommentCreate,
    use_case: CreateCommentUseCase = Depends(create_comment_use_case),
    current_user: User = Depends(get_current_user),
) -> CommentResponse:
    new_comment = await use_case.execute(post_id, comment_in, current_user)
    return CommentResponse.model_validate(new_comment)


@router.get("/", response_model=List[CommentResponse])
async def get_comments(
    post_id: uuid.UUID,
    use_case: GetCommentsUseCase = Depends(get_comments_use_case),
) -> List[CommentResponse]:
    comments = await use_case.execute(post_id)
    return [CommentResponse.model_validate(c) for c in comments]
