import uuid
from typing import List
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse

from src.schemas.posts import PostCreate, PostResponse, PostUpdate
from src.api.dependencies import (
    create_post_use_case,
    delete_post_use_case,
    get_post_use_case,
    get_posts_use_case,
    update_post_use_case,
    update_post_image_use_case,
)
from src.domain.post.use_cases.create_post import CreatePostUseCase
from src.domain.post.use_cases.delete_post import DeletePostUseCase
from src.domain.post.use_cases.get_post import GetPostUseCase
from src.domain.post.use_cases.get_posts import GetPostsUseCase
from src.domain.post.use_cases.update_post import UpdatePostUseCase
from src.domain.post.use_cases.update_post_image import UpdatePostImageUseCase
from src.db.models.users import User
from src.services.auth import get_current_user
from src.core.config import settings

router = APIRouter()

Path(settings.IMAGE_UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found during delete"
        )
    return


@router.post(
    "/{post_id}/image", response_model=PostResponse, status_code=status.HTTP_200_OK
)
async def upload_post_image(
    post_id: uuid.UUID,
    file: UploadFile = File(...),
    use_case: UpdatePostImageUseCase = Depends(update_post_image_use_case),
    current_user: User = Depends(get_current_user),
) -> PostResponse:
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed",
        )

    file_extension = file.filename.split(".")[-1]
    file_name = f"{post_id}.{file_extension}"
    file_path = Path(settings.IMAGE_UPLOAD_DIR) / file_name

    with open(file_path, "wb") as buffer:
        while content := await file.read(1024):
            buffer.write(content)

    db_image_path = str(file_path)
    updated_post = await use_case.execute(post_id, db_image_path, current_user)
    return PostResponse.model_validate(updated_post)


@router.get("/{post_id}/image", response_class=FileResponse)
async def get_post_image(
    post_id: uuid.UUID,
    use_case: GetPostUseCase = Depends(get_post_use_case),
):
    post = await use_case.execute(post_id)
    if post is None or post.image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post image not found"
        )

    file_path = Path(post.image)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post image file not found on server",
        )
    return FileResponse(file_path)
