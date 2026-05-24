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
from src.db.db import database
from src.db.models.users import User
from src.db.repositories.users import UserRepository
from src.db.repositories.refresh_token import RefreshTokenRepository
from src.resources.auth import oauth2_scheme


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    username: str | None = None


async def create_refresh_token(user_id: uuid.UUID, session: AsyncSession) -> str:
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_string = secrets.token_urlsafe(32)
    refresh_token_repo = RefreshTokenRepository(session)
    await refresh_token_repo.create(
        {
            "token": refresh_token_string,
            "user_id": user_id,
            "expires_at": datetime.utcnow() + expires_delta,
        }
    )
    return refresh_token_string


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
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

    async with database.session() as session:
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
