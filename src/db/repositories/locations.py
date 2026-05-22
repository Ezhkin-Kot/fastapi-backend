from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.locations import Location
from src.db.repositories.base import BaseRepository


class LocationRepository(BaseRepository[Location]):
    def __init__(self, session: AsyncSession):
        super().__init__(Location, session)
