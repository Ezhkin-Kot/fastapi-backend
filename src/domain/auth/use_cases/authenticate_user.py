import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.db.models.users import User
from src.db.repositories.users import UserRepository
from src.resources.auth import verify_password
from src.services.auth import create_refresh_token, Token
from src.domain.auth.use_cases.create_access_token import CreateAccessTokenUseCase


class AuthenticateUserUseCase:
    def __init__(
        self,
        create_access_token_use_case: CreateAccessTokenUseCase,
        session: AsyncSession,
        redis_client: Redis,
    ):
        self.create_access_token_use_case = create_access_token_use_case
        self.session = session
        self.user_repository = UserRepository(session)
        self.redis_client = redis_client

    async def execute(self, username: str, password: str) -> Token | None:
        user = await self.user_repository.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None

        access_token = self.create_access_token_use_case.execute(
            data={"sub": user.username}
        )
        refresh_token = await create_refresh_token(user.id, self.redis_client)

        return Token(
            access_token=access_token, token_type="bearer", refresh_token=refresh_token
        )
