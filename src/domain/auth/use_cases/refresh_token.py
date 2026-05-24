import uuid
from datetime import datetime, timedelta
from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CredentialsException
from src.db.repositories.refresh_token import RefreshTokenRepository
from src.db.repositories.users import UserRepository
from src.services.auth import create_refresh_token, Token
from src.domain.auth.use_cases.create_access_token import CreateAccessTokenUseCase


class RefreshTokenUseCase:
    def __init__(
        self,
        create_access_token_use_case: CreateAccessTokenUseCase,
        refresh_token_repository: RefreshTokenRepository,
        user_repository: UserRepository,
        session: AsyncSession,
    ):
        self.create_access_token_use_case = create_access_token_use_case
        self.refresh_token_repository = refresh_token_repository
        self.user_repository = user_repository
        self.session = session

    async def execute(self, refresh_token_string: str) -> Token:
        refresh_token = await self.refresh_token_repository.get_by_token(
            refresh_token_string
        )

        if not refresh_token:
            raise CredentialsException("Invalid refresh token")
        if refresh_token.revoked_at:
            raise CredentialsException("Refresh token revoked")
        if refresh_token.expires_at < datetime.utcnow():
            raise CredentialsException("Refresh token expired")

        user = await self.user_repository.get(refresh_token.user_id)
        if not user:
            raise CredentialsException("User not found")

        # Generate new access token
        new_access_token = self.create_access_token_use_case.execute(
            data={"sub": user.username}
        )

        # Generate new refresh token
        new_refresh_token = await create_refresh_token(user.id, self.session)

        # Revoke the old refresh token
        await self.refresh_token_repository.revoke(refresh_token)

        return Token(
            access_token=new_access_token,
            token_type="bearer",
            refresh_token=new_refresh_token,
        )

