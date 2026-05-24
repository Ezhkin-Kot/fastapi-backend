import uuid
from redis.asyncio import Redis

from src.core.exceptions import CredentialsException
from src.db.repositories.users import UserRepository
from src.services.auth import create_refresh_token, Token
from src.domain.auth.use_cases.create_access_token import CreateAccessTokenUseCase


class RefreshTokenUseCase:
    def __init__(
        self,
        create_access_token_use_case: CreateAccessTokenUseCase,
        user_repository: UserRepository,
        redis_client: Redis,
    ):
        self.create_access_token_use_case = create_access_token_use_case
        self.user_repository = user_repository
        self.redis_client = redis_client

    async def execute(self, refresh_token_string: str) -> Token:
        user_id_bytes = await self.redis_client.get(f"refresh:{refresh_token_string}")
        if not user_id_bytes:
            raise CredentialsException("Invalid or expired refresh token")

        await self.redis_client.delete(f"refresh:{refresh_token_string}")

        user_id = uuid.UUID(user_id_bytes.decode("utf-8"))
        user = await self.user_repository.get(user_id)
        if not user:
            raise CredentialsException("User not found")

        new_access_token = self.create_access_token_use_case.execute(
            data={"sub": user.username}
        )

        new_refresh_token = await create_refresh_token(
            user_id=user.id, redis_client=self.redis_client
        )

        return Token(
            access_token=new_access_token,
            token_type="bearer",
            refresh_token=new_refresh_token,
        )
