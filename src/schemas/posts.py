import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PostBase(BaseModel):
    title: str = Field(max_length=255)
    text: str
    pub_date: datetime
    is_published: bool = True


class PostCreate(PostBase):
    author_id: uuid.UUID
    category_id: uuid.UUID | None = None
    location_id: uuid.UUID | None = None


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    text: str | None = None
    pub_date: datetime | None = None
    is_published: bool | None = None
    category_id: uuid.UUID | None = None
    location_id: uuid.UUID | None = None


class PostResponse(PostBase):
    id: uuid.UUID
    author_id: uuid.UUID
    category_id: uuid.UUID | None
    location_id: uuid.UUID | None
    image: str | None = None
    created_at: datetime
    comment_count: int | None = None
