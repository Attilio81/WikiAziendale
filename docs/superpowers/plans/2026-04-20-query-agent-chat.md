# Query Agent Chat — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aggiungere una tab "Chat" che permette conversazioni multi-turno con un agente AI che legge la wiki e risponde in italiano citando le fonti.

**Architecture:** Un endpoint `POST /api/v1/chat/` istanzia un `QueryAgent` Agno con 3 tool di lettura wiki. La sessione multi-turno è persistita in `chat_sessions.db` via `agno.db.sqlite.SqliteDb`. Il frontend gestisce un `session_id` UUID in `localStorage` e renderizza messaggi con chip-fonte cliccabili.

**Tech Stack:** FastAPI, Agno 1.4 (`SqliteDb`, `add_history_to_context`), SQLAlchemy async, React 18, TypeScript, Tailwind CSS

---

## File Map

| Azione | File |
|--------|------|
| Crea | `backend/app/agents/prompts/query.md` |
| Crea | `backend/app/agents/query.py` |
| Crea | `backend/app/schemas/chat.py` |
| Crea | `backend/app/api/chat.py` |
| Modifica | `backend/app/main.py` |
| Crea | `backend/tests/test_chat.py` |
| Crea | `frontend/src/api/chat.ts` |
| Crea | `frontend/src/pages/Chat.tsx` |
| Modifica | `frontend/src/App.tsx` |

---

## Task 1: Prompt del Query Agent

**Files:**
- Crea: `backend/app/agents/prompts/query.md`

- [ ] **Step 1: Crea il file prompt**

```markdown
Sei un assistente aziendale esperto. Il tuo compito è rispondere a domande sulle procedure aziendali usando esclusivamente le informazioni presenti nella wiki.

## Come operare

1. Usa `search_wiki_pages` per trovare pagine rilevanti alla domanda dell'utente
2. Per ogni pagina rilevante trovata, leggi il contenuto completo con `get_wiki_page`
3. Se la ricerca non trova nulla, usa `list_wiki_pages` per vedere tutte le pagine disponibili e scegli le più pertinenti
4. Rispondi in italiano formale, in modo preciso e conciso
5. Chiudi SEMPRE la risposta con una riga `**Fonti:** slug1, slug2` elencando gli slug di tutte le pagine consultate

## Regole

- Rispondi SOLO con informazioni presenti nelle pagine wiki lette — non inventare nulla
- Se le informazioni richieste non sono nella wiki, dillo esplicitamente: "Non ho trovato informazioni su questo argomento nella wiki aziendale."
- Non rivelare il contenuto grezzo delle pagine — elabora le informazioni in una risposta chiara
- La riga **Fonti:** deve essere l'ultima riga della risposta, separata da una riga vuota
- Elenca solo gli slug effettivamente consultati e utili alla risposta

## Formato risposta

Risposta in italiano formale con la struttura più adatta alla domanda (paragrafi, elenchi puntati, passi numerati).

Alla fine, sempre:

**Fonti:** slug-pagina-1, slug-pagina-2
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/agents/prompts/query.md
git commit -m "feat(chat): add query agent system prompt"
```

---

## Task 2: Query Agent factory + tools

**Files:**
- Crea: `backend/app/agents/query.py`

- [ ] **Step 1: Scrivi i test per i tool**

Crea `backend/tests/test_chat.py` con i test dei tool (senza LLM):

```python
import pytest
from datetime import datetime, timezone
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
```

- [ ] **Step 2: Esegui i test — devono fallire**

```bash
cd backend
pytest tests/test_chat.py -v -k "wiki_pages or search or get_wiki"
```

Expected: `ModuleNotFoundError: No module named 'app.agents.query'`

- [ ] **Step 3: Implementa `query.py`**

Crea `backend/app/agents/query.py`:

```python
from pathlib import Path
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.procedure_wiki import ProcedureWiki


def make_query_tools(db: AsyncSession) -> tuple[list[Callable], None]:
    """Return (tools, None). Tools are async closures that read wiki pages."""

    async def list_wiki_pages() -> str:
        """List all wiki pages with slug and title."""
        result = await db.execute(select(ProcedureWiki.slug, ProcedureWiki.titolo))
        rows = result.all()
        if not rows:
            return "Nessuna pagina wiki disponibile."
        lines = [f"- slug='{r.slug}' | titolo='{r.titolo}'" for r in rows]
        return "Pagine wiki disponibili:\n" + "\n".join(lines)

    async def search_wiki_pages(query: str) -> str:
        """Search wiki pages by keyword in title or content. Returns matching slugs and titles."""
        pattern = f"%{query}%"
        result = await db.execute(
            select(ProcedureWiki.slug, ProcedureWiki.titolo).where(
                or_(
                    ProcedureWiki.titolo.ilike(pattern),
                    ProcedureWiki.contenuto_md.ilike(pattern),
                )
            ).limit(10)
        )
        rows = result.all()
        if not rows:
            return f"Nessuna pagina trovata per la ricerca '{query}'."
        lines = [f"- slug='{r.slug}' | titolo='{r.titolo}'" for r in rows]
        return f"Pagine trovate per '{query}':\n" + "\n".join(lines)

    async def get_wiki_page(slug: str) -> str:
        """Get the full markdown content of a wiki page by its slug."""
        result = await db.execute(select(ProcedureWiki).where(ProcedureWiki.slug == slug))
        page = result.scalar_one_or_none()
        if not page:
            return f"Errore: pagina wiki '{slug}' non trovata."
        links_str = ", ".join(page.links or [])
        return (
            f"Slug: {page.slug}\n"
            f"Titolo: {page.titolo}\n"
            f"Links correlati: {links_str}\n\n"
            f"Contenuto:\n{page.contenuto_md}"
        )

    return [list_wiki_pages, search_wiki_pages, get_wiki_page], None


def make_query_agent(db: AsyncSession, session_id: str):
    """Return an Agno Agent configured for wiki Q&A with session persistence."""
    from agno.agent import Agent
    from agno.db.sqlite import SqliteDb
    from app.core.llm import get_llm_model
    from app.config import get_settings

    settings = get_settings()
    db_url = settings.DATABASE_URL.replace("sqlite:///", "")
    sessions_path = str(Path(db_url).parent / "chat_sessions.db")

    tools, _ = make_query_tools(db)
    prompt_path = Path(__file__).parent / "prompts" / "query.md"
    system_prompt = prompt_path.read_text(encoding="utf-8")

    agent = Agent(
        model=get_llm_model("query"),
        tools=tools,
        instructions=system_prompt,
        db=SqliteDb(db_file=sessions_path),
        session_id=session_id,
        add_history_to_context=True,
        num_history_runs=5,
        store_history_messages=True,
        markdown=True,
        debug_mode=False,
    )
    return agent
```

- [ ] **Step 4: Esegui i test — devono passare**

```bash
cd backend
pytest tests/test_chat.py -v -k "wiki_pages or search or get_wiki"
```

Expected: 7 test PASSED

- [ ] **Step 5: Commit**

```bash
git add backend/app/agents/query.py backend/tests/test_chat.py
git commit -m "feat(chat): add query agent with wiki read tools"
```

---

## Task 3: Schema e helper di parsing

**Files:**
- Crea: `backend/app/schemas/chat.py`
- Test già in `backend/tests/test_chat.py`

- [ ] **Step 1: Aggiungi test di parsing a `test_chat.py`**

Apri `backend/tests/test_chat.py` e aggiungi in fondo:

```python
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
```

- [ ] **Step 2: Esegui — devono fallire**

```bash
cd backend
pytest tests/test_chat.py -v -k "extract or clean_answer"
```

Expected: `ImportError: cannot import name 'extract_sources' from 'app.api.chat'`

- [ ] **Step 3: Crea lo schema chat**

Crea `backend/app/schemas/chat.py`:

```python
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    session_id: str
```

- [ ] **Step 4: Crea `backend/app/api/chat.py` con helper**

```python
import re
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import verify_api_key
from app.schemas.chat import ChatRequest, ChatResponse
from app.agents.query import make_query_agent

router = APIRouter()


def extract_sources(text: str) -> list[str]:
    match = re.search(r'\*\*Fonti:\*\*\s*(.+?)$', text, re.MULTILINE | re.IGNORECASE)
    if not match:
        return []
    return [s.strip() for s in match.group(1).split(',') if s.strip()]


def clean_answer(text: str) -> str:
    return re.sub(r'\n?\*\*Fonti:\*\*\s*.+$', '', text, flags=re.MULTILINE | re.IGNORECASE).strip()


@router.post("/", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    agent = make_query_agent(db, body.session_id)
    run_response = await agent.arun(body.message)
    raw = run_response.content or ""
    return ChatResponse(
        answer=clean_answer(raw),
        sources=extract_sources(raw),
        session_id=body.session_id,
    )
```

- [ ] **Step 5: Esegui i test di parsing — devono passare**

```bash
cd backend
pytest tests/test_chat.py -v -k "extract or clean_answer"
```

Expected: 4 test PASSED

- [ ] **Step 6: Commit**

```bash
git add backend/app/schemas/chat.py backend/app/api/chat.py backend/tests/test_chat.py
git commit -m "feat(chat): add chat schema, endpoint skeleton, and source parsing"
```

---

## Task 4: Endpoint REST + registrazione router

**Files:**
- Modifica: `backend/app/main.py`

- [ ] **Step 1: Aggiungi test endpoint a `test_chat.py`**

```python
from unittest.mock import AsyncMock, MagicMock, patch


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
```

- [ ] **Step 2: Esegui — devono fallire**

```bash
cd backend
pytest tests/test_chat.py -v -k "chat_missing or chat_no_api or chat_returns"
```

Expected: FAIL con `404 Not Found` (router non ancora registrato)

- [ ] **Step 3: Registra il router in `main.py`**

Apri `backend/app/main.py`. Dopo l'import dei router esistenti aggiungi:

```python
from app.api.chat import router as chat_router
```

Dopo `app.include_router(wiki_router, ...)` aggiungi:

```python
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
```

- [ ] **Step 4: Esegui tutti i test — devono passare**

```bash
cd backend
pytest tests/test_chat.py -v
```

Expected: tutti i test PASSED

- [ ] **Step 5: Esegui la suite completa per regressioni**

```bash
cd backend
pytest tests/ -v
```

Expected: tutti i test PASSED (nessuna regressione)

- [ ] **Step 6: Commit**

```bash
git add backend/app/main.py backend/tests/test_chat.py
git commit -m "feat(chat): register chat router, complete backend"
```

---

## Task 5: Frontend — API client

**Files:**
- Crea: `frontend/src/api/chat.ts`

- [ ] **Step 1: Crea il client**

```typescript
import { BASE_URL, defaultHeaders, handleResponse } from './client'

export interface ChatResponse {
  answer: string
  sources: string[]
  session_id: string
}

export async function sendMessage(
  message: string,
  session_id: string,
): Promise<ChatResponse> {
  const res = await fetch(`${BASE_URL}/chat/`, {
    method: 'POST',
    headers: defaultHeaders,
    body: JSON.stringify({ message, session_id }),
  })
  return handleResponse<ChatResponse>(res)
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/api/chat.ts
git commit -m "feat(chat): add frontend chat API client"
```

---

## Task 6: Frontend — Chat page

**Files:**
- Crea: `frontend/src/pages/Chat.tsx`

- [ ] **Step 1: Crea il componente**

```tsx
import { useState, useRef, useEffect } from 'react'
import { sendMessage } from '../api/chat'

const SESSION_KEY = 'wiki_chat_session_id'

type Message = {
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
}

interface ChatProps {
  onNavigateToWiki: (slug: string) => void
}

export function Chat({ onNavigateToWiki }: ChatProps) {
  const [sessionId] = useState<string>(() => {
    const stored = localStorage.getItem(SESSION_KEY)
    if (stored) return stored
    const id = crypto.randomUUID()
    localStorage.setItem(SESSION_KEY, id)
    return id
  })

  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        'Ciao! Posso rispondere a domande sulle procedure aziendali. Cosa vuoi sapere?',
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSend() {
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setLoading(true)
    try {
      const data = await sendMessage(text, sessionId)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.answer, sources: data.sources },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Errore di connessione. Riprova.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-72px)]">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4 max-w-3xl mx-auto w-full">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded px-4 py-3 text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-nav text-white'
                  : 'bg-white border border-gray-200 text-gray-800'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {msg.sources.map((slug) => (
                    <button
                      key={slug}
                      onClick={() => onNavigateToWiki(slug)}
                      className="text-xs bg-accent/10 text-accent border border-accent/30 px-2 py-0.5 rounded hover:bg-accent hover:text-white transition-colors font-mono"
                    >
                      {slug}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded px-4 py-3">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 bg-white px-6 py-4">
        <div className="max-w-3xl mx-auto flex gap-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            placeholder="Scrivi una domanda sulle procedure aziendali..."
            rows={1}
            className="flex-1 resize-none border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-accent disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-5 py-2 bg-nav text-white text-sm font-mono hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ borderRadius: '2px' }}
          >
            Invia
          </button>
        </div>
        <p className="text-center text-xs text-gray-400 mt-2 font-mono">
          Invio per inviare · Shift+Invio per andare a capo
        </p>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/Chat.tsx
git commit -m "feat(chat): add Chat page component with source chips"
```

---

## Task 7: Frontend — App.tsx con tab Chat e navigazione

**Files:**
- Modifica: `frontend/src/App.tsx`

- [ ] **Step 1: Aggiorna App.tsx**

Sostituisci il contenuto di `frontend/src/App.tsx`:

```tsx
import { useState } from 'react'
import { Procedures } from './pages/Procedures'
import { Wiki } from './pages/Wiki'
import { Chat } from './pages/Chat'

type Page = 'procedures' | 'wiki' | 'chat'

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('procedures')
  const [wikiSlug, setWikiSlug] = useState<string | undefined>(undefined)

  function handleNavigateToWiki(slug: string) {
    setWikiSlug(slug)
    setCurrentPage('wiki')
  }

  function handleNavClick(page: Page) {
    setCurrentPage(page)
    if (page !== 'wiki') setWikiSlug(undefined)
  }

  const navLink = (page: Page, label: string) => (
    <button
      onClick={() => handleNavClick(page)}
      className={`text-sm transition-colors pb-0.5 ${
        currentPage === page
          ? 'text-white border-b border-accent'
          : 'text-white/50 hover:text-white/80'
      }`}
    >
      {label}
    </button>
  )

  return (
    <div className="min-h-screen bg-bg">
      <nav className="bg-nav text-white border-b-2 border-accent">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-baseline gap-8">
          <span className="font-display text-xl font-light tracking-wide text-white/90">
            Wiki<span className="text-accent font-semibold">Aziendale</span>
          </span>
          <div className="flex gap-6">
            {navLink('procedures', 'Procedure')}
            {navLink('wiki', 'Wiki')}
            {navLink('chat', 'Chat')}
          </div>
        </div>
      </nav>

      {currentPage === 'procedures' && (
        <main className="max-w-7xl mx-auto px-6 py-10">
          <Procedures />
        </main>
      )}
      {currentPage === 'wiki' && (
        <Wiki initialSlug={wikiSlug} />
      )}
      {currentPage === 'chat' && (
        <main className="max-w-7xl mx-auto">
          <Chat onNavigateToWiki={handleNavigateToWiki} />
        </main>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Aggiorna Wiki.tsx per accettare `initialSlug`**

Apri `frontend/src/pages/Wiki.tsx`. Trova la riga che definisce il componente (es. `export function Wiki()`) e aggiorna la firma:

```tsx
interface WikiProps {
  initialSlug?: string
}

export function Wiki({ initialSlug }: WikiProps) {
```

Poi trova lo `useState` che gestisce la pagina selezionata (di solito qualcosa come `const [selectedSlug, setSelectedSlug] = useState<string | undefined>(undefined)`) e cambialo in:

```tsx
const [selectedSlug, setSelectedSlug] = useState<string | undefined>(initialSlug)
```

- [ ] **Step 3: Verifica che TypeScript compili senza errori**

```bash
cd frontend
npx tsc --noEmit
```

Expected: nessun errore

- [ ] **Step 4: Avvia il dev server e testa manualmente**

```bash
cd frontend
npm run dev -- --port 5175
```

Verifica:
- Tab "Chat" appare nella navbar
- Inviando un messaggio appare il loading (tre puntini)
- La risposta viene mostrata (serve LM Studio attivo)
- I chip delle fonti aprono la tab Wiki sulla pagina corretta

- [ ] **Step 5: Commit finale**

```bash
git add frontend/src/App.tsx frontend/src/pages/Wiki.tsx
git commit -m "feat(chat): wire Chat tab in App with wiki navigation"
```

---

## Task 8: Push

- [ ] **Step 1: Push**

```bash
git push origin master
```
