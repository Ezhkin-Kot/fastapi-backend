from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.users import UserCreate
from src.db.models.users import User
from src.db.repositories.users import UserRepository
from src.resources.auth import get_password_hash


class CreateUserUseCase:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def execute(self, user_in: UserCreate) -> User:
        user_data = user_in.model_dump()
        password_plain = user_in.password.get_secret_value()
        user_data["hashed_password"] = get_password_hash(password_plain)
        del user_data["password"]

        new_user = await self.repository.create(user_data)
        return new_user
