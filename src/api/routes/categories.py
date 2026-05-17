from typing import List

from fastapi import APIRouter, Depends

from src.api.dependencies import get_posts_by_category_use_case
from src.domain.post.use_cases.get_posts_by_category import GetPostsByCategoryUseCase
from src.schemas.posts import PostResponse

router = APIRouter()


@router.get("/{slug}/posts", response_model=List[PostResponse])
async def get_posts_by_category(
    slug: str,
    use_case: GetPostsByCategoryUseCase = Depends(get_posts_by_category_use_case),
) -> List[PostResponse]:
    posts = await use_case.execute(slug)
    return [PostResponse.model_validate(p) for p in posts]
