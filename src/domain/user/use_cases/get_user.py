import uuid

from src.db.db import database
from src.db.models.users import User
from src.db.repositories.users import UserRepository
from src.core.exceptions import NotFoundError


class GetUserUseCase:
    def __init__(self):
        pass

    async def execute(self, user_id: uuid.UUID) -> User:
        async with database.session() as session:
            repo = UserRepository(session)
            user = await repo.get_by_id_with_posts(user_id)
            if not user:
                raise NotFoundError(message="User not found")
            return user
