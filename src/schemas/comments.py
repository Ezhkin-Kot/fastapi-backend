import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    text: str | None = None


class CommentResponse(CommentBase):
    id: uuid.UUID
    post_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
