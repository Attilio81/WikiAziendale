import uuid
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from app.core.db import Base
from app.models.procedure_raw import ProcedureRaw
from app.models.procedure_wiki import ProcedureWiki
from app.models.wiki_index import WikiIndex


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
async def raw_proc(db):
    proc = ProcedureRaw(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        titolo="Ricezione Merci",
        categoria="Magazzino",
        contenuto_md="## Ricezione\n\nPassi 1-3.",
        tags=["magazzino"],
    )
    db.add(proc)
    await db.commit()
    return proc


async def test_get_raw_procedure_found(db, raw_proc):
    from app.agents.compiler import make_compiler_tools
    tools, _ = make_compiler_tools(db, "qwen/qwen3-8b")
    get_raw = tools[0]  # get_raw_procedure
    result = await get_raw("00000000-0000-0000-0000-000000000001")
    assert "Ricezione Merci" in result
    assert "Magazzino" in result


async def test_get_raw_procedure_not_found(db):
    from app.agents.compiler import make_compiler_tools
    tools, _ = make_compiler_tools(db, "qwen/qwen3-8b")
    result = await tools[0]("00000000-0000-0000-0000-000000000099")
    assert "non trovata" in result


async def test_list_wiki_pages_empty(db):
    from app.agents.compiler import make_compiler_tools
    tools, _ = make_compiler_tools(db, "qwen/qwen3-8b")
    result = await tools[1]()  # list_wiki_pages
    assert "Nessuna pagina" in result


async def test_list_wiki_pages_with_data(db):
    from app.agents.compiler import make_compiler_tools
    tools, _ = make_compiler_tools(db, "qwen/qwen3-8b")
    upsert = tools[3]
    await upsert("ricezione-merci", "Ricezione Merci", "# Ricezione", [], [])
    await db.flush()
    result = await tools[1]()
    assert "ricezione-merci" in result


async def test_get_wiki_page_not_found(db):
    from app.agents.compiler import make_compiler_tools
    tools, _ = make_compiler_tools(db, "qwen/qwen3-8b")
    result = await tools[2]("no-such-slug")  # get_wiki_page
    assert "non trovata" in result


async def test_upsert_creates_page(db):
    from app.agents.compiler import make_compiler_tools
    tools, state = make_compiler_tools(db, "qwen/qwen3-8b")
    upsert = tools[3]
    result = await upsert(
        "ricezione-merci", "Ricezione Merci", "# Ricezione\n\nContenuto.",
        ["gestione-nc"], ["00000000-0000-0000-0000-000000000001"],
    )
    assert "creata" in result
    assert "ricezione-merci" in state["affected_slugs"]
    await db.flush()
    r = await db.execute(select(ProcedureWiki).where(ProcedureWiki.slug == "ricezione-merci"))
    page = r.scalar_one_or_none()
    assert page is not None
    assert page.compilation_model == "qwen/qwen3-8b"
    assert page.version == 1


async def test_upsert_updates_existing_page(db):
    from app.agents.compiler import make_compiler_tools
    tools, _ = make_compiler_tools(db, "qwen/qwen3-8b")
    upsert = tools[3]
    await upsert("ricezione-merci", "Original", "# Orig", [], [])
    await db.flush()
    result = await upsert("ricezione-merci", "Updated", "# Updated", [], [])
    assert "aggiornata" in result
    await db.flush()
    r = await db.execute(select(ProcedureWiki).where(ProcedureWiki.slug == "ricezione-merci"))
    page = r.scalar_one()
    assert page.titolo == "Updated"
    assert page.version == 2


async def test_delete_wiki_page(db):
    from app.agents.compiler import make_compiler_tools
    tools, _ = make_compiler_tools(db, "qwen/qwen3-8b")
    upsert, delete = tools[3], tools[4]
    await upsert("to-delete", "To Delete", "# Del", [], [])
    await db.flush()
    result = await delete("to-delete")
    assert "eliminata" in result
    await db.flush()
    r = await db.execute(select(ProcedureWiki).where(ProcedureWiki.slug == "to-delete"))
    assert r.scalar_one_or_none() is None


async def test_delete_wiki_page_not_found(db):
    from app.agents.compiler import make_compiler_tools
    tools, _ = make_compiler_tools(db, "qwen/qwen3-8b")
    result = await tools[4]("nonexistent")
    assert "non trovata" in result


async def test_rebuild_wiki_index(db):
    from app.agents.compiler import make_compiler_tools
    tools, _ = make_compiler_tools(db, "qwen/qwen3-8b")
    upsert, rebuild = tools[3], tools[5]
    await upsert("page-a", "Pagina A", "# A", [], [])
    await upsert("page-b", "Pagina B", "# B", [], [])
    await db.flush()
    result = await rebuild()
    assert "ricostruito" in result
    index = await db.get(WikiIndex, 1)
    assert index is not None
    assert "Pagina A" in index.tree_md
    assert "Pagina B" in index.tree_md


async def test_rebuild_wiki_index_empty(db):
    from app.agents.compiler import make_compiler_tools
    tools, _ = make_compiler_tools(db, "qwen/qwen3-8b")
    result = await tools[5]()
    assert "0" in result or "ricostruito" in result
    index = await db.get(WikiIndex, 1)
    assert index is not None
