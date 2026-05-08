import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.comments import CommentCreate, CommentResponse
from src.core.db import get_async_session
from src.domain.comment.use_cases.create_comment import CreateCommentUseCase
from src.domain.comment.use_cases.get_comments import GetCommentsUseCase
from src.models.users import User
from src.services.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: uuid.UUID,
    comment_in: CommentCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> CommentResponse:
    use_case = CreateCommentUseCase(db)
    new_comment = await use_case.execute(post_id, comment_in, current_user)
    return new_comment


@router.get("/", response_model=List[CommentResponse])
async def get_comments(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
) -> List[CommentResponse]:
    use_case = GetCommentsUseCase(db)
    return await use_case.execute(post_id)
