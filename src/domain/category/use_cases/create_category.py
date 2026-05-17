from src.db.db import database
from src.db.models.categories import Category
from src.db.repositories.categories import CategoryRepository
from src.schemas.categories import CategoryCreate


class CreateCategoryUseCase:
    def __init__(self):
        pass

    async def execute(self, category_in: CategoryCreate) -> Category:
        async with database.session() as session:
            repo = CategoryRepository(session)
            category_data = category_in.model_dump()
            new_category = await repo.create(category_data)
            return new_category
