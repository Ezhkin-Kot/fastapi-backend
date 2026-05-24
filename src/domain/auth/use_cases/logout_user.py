import uuid
from typing import Optional

from src.db.repositories.refresh_token import RefreshTokenRepository


class LogoutUserUseCase:
    def __init__(self, refresh_token_repository: RefreshTokenRepository):
        self.refresh_token_repository = refresh_token_repository

    async def execute(
        self, user_id: uuid.UUID, refresh_token_string: Optional[str] = None
    ) -> None:
        if refresh_token_string:
            refresh_token = await self.refresh_token_repository.get_by_token(
                refresh_token_string
            )
            if refresh_token and refresh_token.user_id == user_id:
                await self.refresh_token_repository.revoke(refresh_token)
        else:
            await self.refresh_token_repository.revoke_all_for_user(user_id)

