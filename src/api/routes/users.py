import uuid
from typing import List

from fastapi import APIRouter, Depends, status

from src.schemas.users import UserCreate, UserResponse, UserUpdate
from src.api.dependencies import create_user_use_case, get_user_use_case
from src.db.db import database
from src.domain.user.use_cases.create_user import CreateUserUseCase
from src.domain.user.use_cases.get_user import GetUserUseCase
from src.db.models.users import User
from src.db.repositories.users import UserRepository
from src.services.auth import get_current_user
from src.core.exceptions import NotFoundError, ForbiddenError

router = APIRouter()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_in: UserCreate, use_case: CreateUserUseCase = Depends(create_user_use_case)
):
    new_user = await use_case.execute(user_in)
    return new_user


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(
    current_user: User = Depends(get_current_user),
) -> List[UserResponse]:
    async with database.session() as session:
        repo = UserRepository(session)
        users = await repo.get_all()
        return [UserResponse.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    use_case: GetUserUseCase = Depends(get_user_use_case),
):
    user = await use_case.execute(user_id=user_id)
    return user


@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
):
    if user_id != current_user.id:
        raise ForbiddenError(message="You can only update your own profile")

    async with database.session() as session:
        repo = UserRepository(session)

        db_user = await repo.get(user_id)
        if db_user is None:
            raise NotFoundError(message="User not found")

        update_data = user_update.model_dump(exclude_unset=True)
        updated_user = await repo.update(db_user, update_data)
        return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
):
    if user_id != current_user.id:
        raise ForbiddenError(message="You can only delete your own profile")

    async with database.session() as session:
        repo = UserRepository(session)

        db_user = await repo.get(user_id)
        if db_user is None:
            raise NotFoundError(message="User not found")

        await repo.delete(db_user)
    return
