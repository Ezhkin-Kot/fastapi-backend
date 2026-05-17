import uuid
from datetime import datetime, timezone
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.db import Base


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(unique=True)
    is_published: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=datetime.now(timezone.utc)
    )

    posts: Mapped[List["Post"]] = relationship(back_populates="location")
