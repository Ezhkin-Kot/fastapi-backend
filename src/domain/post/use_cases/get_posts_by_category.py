from typing import List, Tuple, Sequence

from src.db.db import database
from src.db.models.posts import Post
from src.db.repositories.posts import PostRepository


class GetPostsByCategoryUseCase:
    def __init__(self):
        pass

    async def execute(
        self, slug: str, page: int = 1, size: int = 10
    ) -> Tuple[Sequence[Post], int]:
        skip = (page - 1) * size
        async with database.session() as session:
            repo = PostRepository(session)
            return await repo.get_by_category_slug(slug=slug, skip=skip, limit=size)
