from src.db.db import database
from src.db.models.users import User
from src.db.repositories.users import UserRepository
from src.resources.auth import verify_password


class AuthenticateUserUseCase:
    def __init__(self):
        pass

    async def execute(self, username: str, password: str) -> User | None:
        async with database.session() as session:
            self.repository = UserRepository(session)
            user = await self.repository.get_by_username(username)
            if not user:
                return None
            if not verify_password(password, user.hashed_password):
                return None
            return user
