import uuid
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.db import Base
from app.models.procedure_raw import ProcedureRaw
from app.models.compilation_log import CompilationLog


PROC_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


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
async def procedure(db):
    proc = ProcedureRaw(
        id=PROC_ID,
        titolo="Test",
        categoria="Q",
        contenuto_md="## Test",
        tags=[],
    )
    db.add(proc)
    await db.commit()
    return proc


async def test_run_compilation_success_updates_status(db, procedure):
    mock_agent = MagicMock()
    mock_agent.arun = AsyncMock(return_value=MagicMock(content="Completato."))
    mock_state = {"affected_slugs": ["test-slug"]}

    with patch("app.services.compilation.make_compiler_agent", return_value=(mock_agent, mock_state)):
        from app.services.compilation import run_compilation
        log = await run_compilation([PROC_ID], "create", db)

    assert log.status == "completed"
    assert log.trigger_type == "create"
    assert "test-slug" in log.affected_wiki_slugs
    assert str(PROC_ID) in log.affected_raw_ids

    proc = await db.get(ProcedureRaw, PROC_ID)
    assert proc.compilation_status == "compiled"
    assert proc.compilation_error is None


async def test_run_compilation_failure_updates_status(db, procedure):
    mock_agent = MagicMock()
    mock_agent.arun = AsyncMock(side_effect=Exception("LLM unreachable"))
    mock_state = {"affected_slugs": []}

    with patch("app.services.compilation.make_compiler_agent", return_value=(mock_agent, mock_state)):
        from app.services.compilation import run_compilation
        log = await run_compilation([PROC_ID], "create", db)

    assert log.status == "failed"
    assert "LLM unreachable" in log.error

    proc = await db.get(ProcedureRaw, PROC_ID)
    assert proc.compilation_status == "failed"
    assert "LLM unreachable" in proc.compilation_error


async def test_run_compilation_writes_log_to_db(db, procedure):
    mock_agent = MagicMock()
    mock_agent.arun = AsyncMock(return_value=MagicMock(content="OK"))
    mock_state = {"affected_slugs": []}

    with patch("app.services.compilation.make_compiler_agent", return_value=(mock_agent, mock_state)):
        from app.services.compilation import run_compilation
        log = await run_compilation([PROC_ID], "rebuild", db)

    from sqlalchemy import select
    result = await db.execute(select(CompilationLog))
    logs = result.scalars().all()
    assert len(logs) == 1
    assert logs[0].trigger_type == "rebuild"
    assert logs[0].duration_ms is not None
    assert logs[0].duration_ms >= 0
