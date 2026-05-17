from typing import List

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_posts_by_category_use_case
from src.domain.post.use_cases.get_posts_by_category import GetPostsByCategoryUseCase
from src.schemas.posts import PostResponse
from src.schemas.pagination import PaginatedResponse
from src.core.config import settings

router = APIRouter()


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
