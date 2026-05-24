from jose import JWTError, jwt
from pydantic import BaseModel
from starlette import status
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import secrets
from datetime import datetime, timedelta
import uuid

from src.core.config import settings
from src.core.exceptions import ForbiddenError
from src.db.models.users import User
from src.db.repositories.users import UserRepository
from src.resources.auth import oauth2_scheme
from src.db.redis import get_redis_client
from redis.asyncio import Redis
from src.db.db import get_session


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    username: str | None = None


async def create_refresh_token(user_id: uuid.UUID, redis_client: Redis) -> str:
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_string = secrets.token_urlsafe(32)
    await redis_client.set(
        name=f"refresh:{refresh_token_string}",
        value=str(user_id),
        ex=int(expires_delta.total_seconds()),
    )
    return refresh_token_string


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
    redis_client: Redis = Depends(get_redis_client),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if await redis_client.get(f"blocklist:{token}"):
        raise credentials_exception

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user_repository = UserRepository(session)
    user = await user_repository.get_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise ForbiddenError(message="Admin access required")
    return current_user
