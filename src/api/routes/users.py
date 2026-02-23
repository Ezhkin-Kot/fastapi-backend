import datetime
import uuid
from typing import List

from fastapi import APIRouter, HTTPException, status

from schemas.users import UserCreate, UserResponse, UserUpdate

router = APIRouter()

fake_db = []


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    new_user = UserResponse(
        id=uuid.uuid4(),
        created_at=datetime.datetime.now(datetime.timezone.utc),
        **user.model_dump(exclude={"password"}),
    )

    fake_db.append(new_user)

    return new_user


@router.get("/", response_model=List[UserResponse])
async def get_users():
    return fake_db


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: uuid.UUID):
    user = next((user for user in fake_db if user.id == user_id), None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: uuid.UUID, user_update: UserUpdate):
    user_index = next(
        (index for index, user in enumerate(fake_db) if user.id == user_id), None
    )
    if user_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user = fake_db[user_index]
    update_data = user_update.model_dump(exclude_unset=True)
    updated_user = user.model_copy(update=update_data)
    fake_db[user_index] = updated_user

    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: uuid.UUID):
    user_index = next(
        (index for index, user in enumerate(fake_db) if user.id == user_id), None
    )
    if user_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    fake_db.pop(user_index)

    return
