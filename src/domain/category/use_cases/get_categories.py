from typing import Sequence
from src.db.db import database
from src.db.models.categories import Category
from src.db.repositories.categories import CategoryRepository


class GetCategoriesUseCase:
    def __init__(self):
        pass

    async def execute(self) -> Sequence[Category]:
        async with database.session() as session:
            repo = CategoryRepository(session)
            return await repo.get_all()
