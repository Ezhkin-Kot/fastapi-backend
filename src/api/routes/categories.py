import uuid
from typing import List

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import (
    get_posts_by_category_use_case,
    get_categories_use_case,
    get_category_use_case,
)
from src.domain.post.use_cases.get_posts_by_category import GetPostsByCategoryUseCase
from src.domain.category.use_cases.get_categories import GetCategoriesUseCase
from src.domain.category.use_cases.get_category import GetCategoryUseCase
from src.schemas.posts import PostResponse
from src.schemas.categories import CategoryResponse
from src.schemas.pagination import PaginatedResponse
from src.core.config import settings

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
async def get_all_categories(
    use_case: GetCategoriesUseCase = Depends(get_categories_use_case),
):
    categories = await use_case.execute()
    return [CategoryResponse.model_validate(c) for c in categories]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: uuid.UUID,
    use_case: GetCategoryUseCase = Depends(get_category_use_case),
):
    category = await use_case.execute(category_id)
    return CategoryResponse.model_validate(category)


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
