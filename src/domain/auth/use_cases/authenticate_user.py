from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User
from repositories.users import UserRepository
from resources.auth import verify_password


class AuthenticateUserUseCase:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def execute(self, username: str, password: str) -> User | None:
        user = await self.repository.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
