import re
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, SecretStr, validator


class UserBase(BaseModel):
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    username: str = Field(max_length=255)
    email: EmailStr


class UserCreate(UserBase):
    password: SecretStr = Field(min_length=8, max_length=255)

    @validator("password")
    def password_complexity(cls, v: SecretStr):
        password = v.get_secret_value()
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[a-zA-Z]", password):
            raise ValueError("Password must contain at least one letter.")
        return v


class UserUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    username: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None


class UserUpdatePassword(BaseModel):
    current_password: SecretStr = Field(min_length=8, max_length=255)
    new_password: SecretStr = Field(min_length=8, max_length=255)


class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime | None = None
