import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.core.db import Base, get_db


TEST_API_KEY = "dev-change-me"


@pytest.fixture(autouse=True)
def reset_api_key_env():
    """Ensure API_KEY env var and settings cache are in a clean state for each test."""
    from app.config import get_settings
    original = os.environ.get("API_KEY")
    os.environ["API_KEY"] = TEST_API_KEY
    get_settings.cache_clear()
    yield
    if original is None:
        os.environ.pop("API_KEY", None)
    else:
        os.environ["API_KEY"] = original
    get_settings.cache_clear()


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-API-Key": TEST_API_KEY},
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
