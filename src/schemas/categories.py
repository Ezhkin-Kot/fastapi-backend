import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    title: str = Field(max_length=255)
    description: str
    slug: str
    is_published: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    slug: str | None = None
    is_published: bool | None = None


class CategoryResponse(CategoryBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
