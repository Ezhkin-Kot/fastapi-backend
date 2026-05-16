import uuid
from datetime import datetime, timezone
from typing import List
from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.db import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str]
    text: Mapped[str]
    pub_date: Mapped[datetime]
    is_published: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=datetime.now(timezone.utc)
    )
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("categories.id"))
    location_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("locations.id"))

    author: Mapped["User"] = relationship(back_populates="posts")
    category: Mapped["Category"] = relationship()
    location: Mapped["Location"] = relationship()
    comments: Mapped[List["Comment"]] = relationship(back_populates="post")
