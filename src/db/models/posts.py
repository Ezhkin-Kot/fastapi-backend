import uuid
from datetime import datetime, timezone
from typing import List
from sqlalchemy import func, ForeignKey, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from src.db.db import Base
from src.db.models.comments import Comment


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str]
    text: Mapped[str]
    pub_date: Mapped[datetime]
    image: Mapped[str] = mapped_column(String, nullable=True)
    is_published: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=datetime.now(timezone.utc)
    )
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("categories.id"))
    location_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("locations.id"))

    author: Mapped["User"] = relationship(back_populates="posts")
    category: Mapped["Category"] = relationship(back_populates="posts")
    location: Mapped["Location"] = relationship(back_populates="posts")
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )

    @hybrid_property
    def comment_count(self):
        return len(self.comments)

    @comment_count.expression
    def comment_count(cls):
        return (
            select(func.count(Comment.id))
            .where(Comment.post_id == cls.id)
            .scalar_subquery()
        )
