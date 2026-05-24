import sys
import os
import asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import create_app
from src.db.db import Base, Database, database

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


test_database = Database()
test_database._engine = engine
test_database._session_factory = sessionmaker(
    bind=test_database._engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

database.session = test_database.session


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    for table in Base.metadata.tables.values():
        table.schema = None
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


import fakeredis.aioredis

from src.db.redis import get_redis_client


@pytest.fixture(scope="function")
async def test_app():
    app = create_app()
    fake_redis_client = fakeredis.aioredis.FakeRedis()

    async def override_get_redis():
        yield fake_redis_client

    app.dependency_overrides[get_redis_client] = override_get_redis
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    await fake_redis_client.aclose()
