import os
import uuid
import pytest
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.core.db import Base, get_db
from app.models.procedure_wiki import ProcedureWiki
from app.models.wiki_index import WikiIndex
from app.models.compilation_log import CompilationLog
from app.models.procedure_raw import ProcedureRaw

TEST_API_KEY = "dev-change-me"


@pytest.fixture(autouse=True)
def reset_env():
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
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def client(db):
    async def _override():
        yield db
    app.dependency_overrides[get_db] = _override
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-API-Key": TEST_API_KEY},
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


async def test_get_wiki_index_empty(client):
    r = await client.get("/api/v1/wiki/index")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == 1
    assert data["tree_md"] is None
    assert data["last_rebuilt_at"] is None


async def test_get_wiki_index_with_data(client, db):
    db.add(WikiIndex(id=1, tree_md="# Indice\n- ricezione-merci", last_rebuilt_at=datetime.now(timezone.utc)))
    await db.commit()
    r = await client.get("/api/v1/wiki/index")
    assert r.status_code == 200
    assert "Indice" in r.json()["tree_md"]


async def test_list_wiki_pages_empty(client):
    r = await client.get("/api/v1/wiki/pages")
    assert r.status_code == 200
    assert r.json() == []


async def test_list_wiki_pages_returns_items(client, db):
    db.add(ProcedureWiki(
        slug="ricezione-merci", titolo="Ricezione Merci",
        contenuto_md="# Ricezione", links=[], source_raw_ids=[],
        last_compiled_at=datetime.now(timezone.utc), compilation_model="qwen/qwen3-8b", version=1,
    ))
    await db.commit()
    r = await client.get("/api/v1/wiki/pages")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["slug"] == "ricezione-merci"
    assert "contenuto_md" not in data[0]  # list view is lightweight


async def test_get_wiki_page_not_found(client):
    r = await client.get("/api/v1/wiki/pages/nonexistent")
    assert r.status_code == 404


async def test_get_wiki_page_found(client, db):
    db.add(ProcedureWiki(
        slug="gestione-nc", titolo="Gestione Non Conformità",
        contenuto_md="# Gestione NC\n\nContenuto.",
        links=["ricezione-merci"], source_raw_ids=["00000000-0000-0000-0000-000000000001"],
        last_compiled_at=datetime.now(timezone.utc), compilation_model="qwen/qwen3-8b", version=1,
    ))
    await db.commit()
    r = await client.get("/api/v1/wiki/pages/gestione-nc")
    assert r.status_code == 200
    data = r.json()
    assert data["slug"] == "gestione-nc"
    assert data["titolo"] == "Gestione Non Conformità"
    assert "contenuto_md" in data
    assert "ricezione-merci" in data["links"]


async def test_trigger_rebuild_no_procedures_returns_202(client):
    r = await client.post("/api/v1/wiki/rebuild")
    assert r.status_code == 202
    assert r.json()["count"] == 0


async def test_trigger_rebuild_with_procedures_returns_202(client, db):
    db.add(ProcedureRaw(
        titolo="Test", categoria="Q", contenuto_md="## Test", tags=[],
    ))
    await db.commit()
    r = await client.post("/api/v1/wiki/rebuild")
    assert r.status_code == 202
    assert r.json()["count"] == 1


async def test_list_compilation_log_empty(client):
    r = await client.get("/api/v1/wiki/compilation-log")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    assert data["items"] == []


async def test_list_compilation_log_with_entries(client, db):
    db.add(CompilationLog(
        triggered_at=datetime.now(timezone.utc),
        trigger_type="create",
        affected_raw_ids=["00000000-0000-0000-0000-000000000001"],
        affected_wiki_slugs=["ricezione-merci"],
        duration_ms=1500,
        model_used="qwen/qwen3-8b",
        status="completed",
    ))
    await db.commit()
    r = await client.get("/api/v1/wiki/compilation-log")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["status"] == "completed"
    assert data["items"][0]["duration_ms"] == 1500


async def test_wiki_requires_api_key(db):
    async def _override():
        yield db
    app.dependency_overrides[get_db] = _override
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        r = await ac.get("/api/v1/wiki/index")
    app.dependency_overrides.clear()
    assert r.status_code == 401
