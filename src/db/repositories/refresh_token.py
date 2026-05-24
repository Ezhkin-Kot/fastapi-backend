import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.refresh_token import RefreshToken
from src.db.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> RefreshToken:
        refresh_token = RefreshToken(**data)
        self.session.add(refresh_token)
        await self.session.flush()
        return refresh_token

    async def revoke(self, refresh_token: RefreshToken) -> RefreshToken:
        refresh_token.revoked_at = func.now()
        await self.session.flush()
        return refresh_token

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .update({"revoked_at": func.now()}, synchronize_session="fetch")
        )
        await self.session.flush()

