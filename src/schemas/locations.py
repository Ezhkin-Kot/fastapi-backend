import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    name: str = Field(max_length=255)
    is_published: bool = True


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    is_published: bool | None = None


class Location(LocationBase):
    id: uuid.UUID
    created_at: datetime
