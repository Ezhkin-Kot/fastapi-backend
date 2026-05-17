import uuid
from src.db.db import database
from src.db.models.categories import Category
from src.db.repositories.categories import CategoryRepository
from src.schemas.categories import CategoryUpdate
from src.core.exceptions import NotFoundError


class UpdateCategoryUseCase:
    def __init__(self):
        pass

    async def execute(
        self, category_id: uuid.UUID, category_update: CategoryUpdate
    ) -> Category:
        async with database.session() as session:
            repo = CategoryRepository(session)
            category = await repo.get(category_id)
            if not category:
                raise NotFoundError("Category not found")

            update_data = category_update.model_dump(exclude_unset=True)
            updated_category = await repo.update(category, update_data)
            return updated_category
