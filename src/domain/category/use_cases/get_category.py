import uuid
from src.db.db import database
from src.db.models.categories import Category
from src.db.repositories.categories import CategoryRepository
from src.core.exceptions import NotFoundError


class GetCategoryUseCase:
    def __init__(self):
        pass

    async def execute(self, category_id: uuid.UUID) -> Category:
        async with database.session() as session:
            repo = CategoryRepository(session)
            category = await repo.get(category_id)
            if not category:
                raise NotFoundError("Category not found")
            return category
