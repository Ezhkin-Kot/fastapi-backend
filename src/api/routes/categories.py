import uuid
from typing import List

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import (
    get_posts_by_category_use_case,
    create_category_use_case,
    get_all_categories_use_case,
    get_category_use_case,
    update_category_use_case,
    delete_category_use_case,
)
from src.domain.post.use_cases.get_posts_by_category import GetPostsByCategoryUseCase
from src.domain.category.use_cases.create_category import CreateCategoryUseCase
from src.domain.category.use_cases.get_all_categories import GetAllCategoriesUseCase
from src.domain.category.use_cases.get_category import GetCategoryUseCase
from src.domain.category.use_cases.update_category import UpdateCategoryUseCase
from src.domain.category.use_cases.delete_category import DeleteCategoryUseCase
from src.schemas.posts import PostResponse
from src.schemas.categories import CategoryResponse, CategoryCreate, CategoryUpdate
from src.schemas.pagination import PaginatedResponse
from src.core.config import settings
from src.db.models.users import User
from src.services.auth import get_current_user
from src.core.exceptions import ForbiddenError

router = APIRouter()


def is_admin(user: User = Depends(get_current_user)):
    if not user.is_superuser:
        raise ForbiddenError("This action requires admin privileges")
    return user


@router.post("/", response_model=CategoryResponse, dependencies=[Depends(is_admin)])
async def create_category(
    category_in: CategoryCreate,
    use_case: CreateCategoryUseCase = Depends(create_category_use_case),
):
    category = await use_case.execute(category_in)
    return CategoryResponse.model_validate(category)


@router.get("/", response_model=PaginatedResponse[CategoryResponse])
async def get_all_categories(
    page: int = 1,
    size: int = Query(default=settings.PAGINATION_SIZE, ge=1, le=100),
    use_case: GetAllCategoriesUseCase = Depends(get_all_categories_use_case),
):
    categories, total = await use_case.execute(page=page, size=size)
    return PaginatedResponse(
        total=total,
        page=page,
        size=size,
        results=[CategoryResponse.model_validate(c) for c in categories],
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: uuid.UUID,
    use_case: GetCategoryUseCase = Depends(get_category_use_case),
):
    category = await use_case.execute(category_id)
    return CategoryResponse.model_validate(category)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    dependencies=[Depends(is_admin)],
)
async def update_category(
    category_id: uuid.UUID,
    category_in: CategoryUpdate,
    use_case: UpdateCategoryUseCase = Depends(update_category_use_case),
):
    category = await use_case.execute(category_id, category_in)
    return CategoryResponse.model_validate(category)


@router.delete("/{category_id}", status_code=204, dependencies=[Depends(is_admin)])
async def delete_category(
    category_id: uuid.UUID,
    use_case: DeleteCategoryUseCase = Depends(delete_category_use_case),
):
    await use_case.execute(category_id)
    return


@router.get("/{slug}/posts", response_model=PaginatedResponse[PostResponse])
async def get_posts_by_category(
    slug: str,
    page: int = 1,
    size: int = Query(default=settings.PAGINATION_SIZE, ge=1, le=100),
    use_case: GetPostsByCategoryUseCase = Depends(get_posts_by_category_use_case),
) -> PaginatedResponse[PostResponse]:
    posts, total = await use_case.execute(slug=slug, page=page, size=size)
    return PaginatedResponse(
        total=total,
        page=page,
        size=size,
        results=[PostResponse.model_validate(p) for p in posts],
    )
