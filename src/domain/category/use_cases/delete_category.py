import uuid
from src.db.db import database
from src.db.repositories.categories import CategoryRepository
from src.core.exceptions import NotFoundError


class DeleteCategoryUseCase:
    def __init__(self):
        pass

    async def execute(self, category_id: uuid.UUID) -> None:
        async with database.session() as session:
            repo = CategoryRepository(session)
            category = await repo.get(category_id)
            if not category:
                raise NotFoundError("Category not found")
            await repo.delete(category)
