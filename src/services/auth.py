from jose import JWTError, jwt
from pydantic import BaseModel
from starlette import status
from fastapi import Depends, HTTPException

from src.core.config import settings
from src.db.db import database
from src.db.models.users import User
from src.db.repositories.users import UserRepository
from src.resources.auth import oauth2_scheme


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


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
