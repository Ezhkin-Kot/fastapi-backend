import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.posts import PostCreate, PostResponse, PostUpdate
from src.api.dependencies import (
    create_post_use_case,
    delete_post_use_case,
    get_post_use_case,
    get_posts_use_case,
    update_post_use_case,
)
from src.domain.post.use_cases.create_post import CreatePostUseCase
from src.domain.post.use_cases.delete_post import DeletePostUseCase
from src.domain.post.use_cases.get_post import GetPostUseCase
from src.domain.post.use_cases.get_posts import GetPostsUseCase
from src.domain.post.use_cases.update_post import UpdatePostUseCase
from src.db.models.users import User
from src.services.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_in: PostCreate,
    use_case: CreatePostUseCase = Depends(create_post_use_case),
    current_user: User = Depends(get_current_user),
) -> PostResponse:
    new_post = await use_case.execute(post_in, current_user)
    return PostResponse.model_validate(new_post)


@router.get("/", response_model=List[PostResponse])
async def get_posts(
    use_case: GetPostsUseCase = Depends(get_posts_use_case),
) -> List[PostResponse]:
    posts = await use_case.execute()
    return [PostResponse.model_validate(p) for p in posts]


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: uuid.UUID,
    use_case: GetPostUseCase = Depends(get_post_use_case),
) -> PostResponse:
    post = await use_case.execute(post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return PostResponse.model_validate(post)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: uuid.UUID,
    post_update: PostUpdate,
    get_use_case: GetPostUseCase = Depends(get_post_use_case),
    update_use_case: UpdatePostUseCase = Depends(update_post_use_case),
    current_user: User = Depends(get_current_user),
) -> PostResponse:
    post = await get_use_case.execute(post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this post",
        )
    updated_post = await update_use_case.execute(post_id, post_update)
    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found during update"
        )
    return PostResponse.model_validate(updated_post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: uuid.UUID,
    get_use_case: GetPostUseCase = Depends(get_post_use_case),
    delete_use_case: DeletePostUseCase = Depends(delete_post_use_case),
    current_user: User = Depends(get_current_user),
):
    post = await get_use_case.execute(post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this post",
        )
    success = await delete_use_case.execute(post_id)
    if not success:
        # This case should ideally not be hit if the first get_use_case succeeded
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found during delete"
        )
    return
