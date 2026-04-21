import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from app.models.procedure_wiki import ProcedureWiki


async def _add_page(db, slug: str, titolo: str, contenuto: str):
    page = ProcedureWiki(
        slug=slug,
        titolo=titolo,
        contenuto_md=contenuto,
        links=[],
        source_raw_ids=[],
        last_compiled_at=datetime.now(timezone.utc),
        compilation_model="test",
        version=1,
    )
    db.add(page)
    await db.commit()
    return page


# --- Tool tests ---

async def test_list_wiki_pages_empty(db_session):
    from app.agents.query import make_query_tools
    tools, _ = make_query_tools(db_session)
    result = await tools[0]()
    assert "Nessuna pagina" in result


async def test_list_wiki_pages_returns_slugs(db_session):
    await _add_page(db_session, "ricezione-merci", "Ricezione Merci", "Contenuto.")
    from app.agents.query import make_query_tools
    tools, _ = make_query_tools(db_session)
    result = await tools[0]()
    assert "ricezione-merci" in result


async def test_search_wiki_pages_finds_by_title(db_session):
    await _add_page(db_session, "ricezione-merci", "Ricezione Merci", "Testo procedura.")
    from app.agents.query import make_query_tools
    tools, _ = make_query_tools(db_session)
    result = await tools[1]("Ricezione")
    assert "ricezione-merci" in result


async def test_search_wiki_pages_finds_by_content(db_session):
    await _add_page(db_session, "gestione-nc", "Gestione NC", "Non conformità modulo NC-01.")
    from app.agents.query import make_query_tools
    tools, _ = make_query_tools(db_session)
    result = await tools[1]("NC-01")
    assert "gestione-nc" in result


async def test_search_wiki_pages_no_results(db_session):
    from app.agents.query import make_query_tools
    tools, _ = make_query_tools(db_session)
    result = await tools[1]("terminequenontrovera")
    assert "Nessuna pagina" in result


async def test_get_wiki_page_returns_content(db_session):
    await _add_page(db_session, "test-slug", "Test", "Contenuto specifico della pagina.")
    from app.agents.query import make_query_tools
    tools, _ = make_query_tools(db_session)
    result = await tools[2]("test-slug")
    assert "Contenuto specifico della pagina." in result


async def test_get_wiki_page_not_found(db_session):
    from app.agents.query import make_query_tools
    tools, _ = make_query_tools(db_session)
    result = await tools[2]("non-esiste")
    assert "non trovata" in result


# --- Parsing tests ---

def test_extract_sources_parses_two_slugs():
    from app.api.chat import extract_sources
    text = "Risposta.\n\n**Fonti:** ricezione-merci, gestione-nc"
    assert extract_sources(text) == ["ricezione-merci", "gestione-nc"]


def test_extract_sources_empty_when_absent():
    from app.api.chat import extract_sources
    assert extract_sources("Risposta senza fonti.") == []


def test_extract_sources_handles_spaces():
    from app.api.chat import extract_sources
    text = "Testo\n**Fonti:**  slug-a ,  slug-b "
    result = extract_sources(text)
    assert result == ["slug-a", "slug-b"]


def test_clean_answer_removes_fonti_line():
    from app.api.chat import clean_answer
    text = "Risposta.\n\n**Fonti:** ricezione-merci"
    result = clean_answer(text)
    assert "**Fonti:**" not in result
    assert "Risposta." in result


# --- Endpoint tests ---

async def test_chat_missing_message_returns_422(client):
    resp = await client.post("/api/v1/chat/", json={"session_id": "abc"})
    assert resp.status_code == 422


async def test_chat_missing_session_id_returns_422(client):
    resp = await client.post("/api/v1/chat/", json={"message": "ciao"})
    assert resp.status_code == 422


async def test_chat_no_api_key_returns_401(client):
    from httpx import AsyncClient, ASGITransport
    from app.main import app as test_app
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as ac:
        resp = await ac.post("/api/v1/chat/", json={"message": "ciao", "session_id": "x"})
    assert resp.status_code == 401


async def test_chat_returns_answer_and_sources(client):
    mock_run = MagicMock()
    mock_run.content = "Procedura in tre passi.\n\n**Fonti:** ricezione-merci, gestione-nc"
    mock_agent = AsyncMock()
    mock_agent.arun = AsyncMock(return_value=mock_run)

    with patch("app.api.chat.make_query_agent", return_value=mock_agent):
        resp = await client.post(
            "/api/v1/chat/",
            json={"message": "Come funziona la ricezione merci?", "session_id": "test-session"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "sources" in data
    assert "ricezione-merci" in data["sources"]
    assert "gestione-nc" in data["sources"]
    assert "**Fonti:**" not in data["answer"]
    assert data["session_id"] == "test-session"
