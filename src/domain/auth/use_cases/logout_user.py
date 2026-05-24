from typing import Optional
from redis.asyncio import Redis
from datetime import datetime, UTC
from jose import jwt, JWTError

from src.core.config import settings


class LogoutUserUseCase:
    def __init__(
        self,
        redis_client: Redis,
    ):
        self.redis_client = redis_client

    async def execute(
        self,
        access_token: str,
        refresh_token_string: Optional[str] = None,
    ) -> None:
        if refresh_token_string:
            await self.redis_client.delete(f"refresh:{refresh_token_string}")

        try:
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                expires_at = datetime.fromtimestamp(exp_timestamp, tz=UTC)
                ttl = expires_at - datetime.now(UTC)
                if ttl.total_seconds() > 0:
                    await self.redis_client.set(
                        f"blocklist:{access_token}", "1", ex=ttl
                    )
        except JWTError:
            pass
