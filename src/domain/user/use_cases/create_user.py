from src.db.db import database
from src.schemas.users import UserCreate
from src.db.models.users import User
from src.db.repositories.users import UserRepository
from src.resources.auth import get_password_hash


class CreateUserUseCase:
    def __init__(self):
        pass

    async def execute(self, user_in: UserCreate) -> User:
        async with database.session() as session:
            repo = UserRepository(session)
            user_data = user_in.model_dump()
            password_plain = user_in.password.get_secret_value()
            user_data["hashed_password"] = get_password_hash(password_plain)
            del user_data["password"]

            new_user = await repo.create(user_data)
            await session.flush()
            await session.refresh(new_user, attribute_names=["posts"])
            return new_user
