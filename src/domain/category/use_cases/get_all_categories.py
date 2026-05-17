from typing import Sequence
from src.db.db import database
from src.db.models.categories import Category
from src.db.repositories.categories import CategoryRepository


class GetAllCategoriesUseCase:
    def __init__(self):
        pass

    async def execute(self, page: int = 1, size: int = 10) -> (Sequence[Category], int):
        skip = (page - 1) * size
        async with database.session() as session:
            repo = CategoryRepository(session)
            return await repo.get_all_paginated(skip=skip, limit=size)
