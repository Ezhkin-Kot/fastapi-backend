import datetime
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from schemas.posts import PostCreate, PostResponse, PostUpdate
from src.models.users import User
from src.services.auth import get_current_user

router = APIRouter()

fake_db = []


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate, current_user: User = Depends(get_current_user)
) -> PostResponse:
    new_post = PostResponse(
        id=uuid.uuid4(),
        created_at=datetime.datetime.now(datetime.timezone.utc),
        **post.model_dump(),
    )

    fake_db.append(new_post)

    return new_post


@router.get("/", response_model=List[PostResponse])
async def get_posts(
    current_user: User = Depends(get_current_user),
) -> List[PostResponse]:
    return fake_db


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: uuid.UUID, current_user: User = Depends(get_current_user)
) -> PostResponse:
    post = next((post for post in fake_db if post.id == post_id), None)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: uuid.UUID,
    post_update: PostUpdate,
    current_user: User = Depends(get_current_user),
) -> PostResponse:
    post_index = next(
        (index for index, post in enumerate(fake_db) if post.id == post_id), None
    )
    if post_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    post = fake_db[post_index]
    update_data = post_update.model_dump(exclude_unset=True)
    updated_post = post.model_copy(update=update_data)
    fake_db[post_index] = updated_post

    return updated_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: uuid.UUID, current_user: User = Depends(get_current_user)
):
    post_index = next(
        (index for index, post in enumerate(fake_db) if post.id == post_id), None
    )
    if post_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    fake_db.pop(post_index)

    return
