import uuid
from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str]
    description: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True)
    is_published: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=datetime.now(timezone.utc)
    )
