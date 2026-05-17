import uuid
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.exceptions import UserAlreadyExistsError
from src.db.models.users import User
from src.db.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_id_with_posts(self, user_id: uuid.UUID) -> User | None:
        query = select(User).where(User.id == user_id).options(joinedload(User.posts))
        return await self.session.scalar(query)

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        return await self.session.scalar(query)

    async def create(self, data: dict) -> User:
        try:
            return await super().create(data)
        except IntegrityError:
            raise UserAlreadyExistsError()

    async def get_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        return await self.session.scalar(query)
