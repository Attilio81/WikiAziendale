# Query Agent Chat — Design Spec

**Data:** 2026-04-20  
**Stato:** Approvato  

---

## Obiettivo

Aggiungere una tab "Chat" all'applicazione Wiki Aziendale che permette agli utenti di fare domande in linguaggio naturale sull'intera wiki. Un agente AI (Agno) legge le pagine rilevanti e risponde in italiano citando le fonti.

---

## Architettura

```
Frontend (Chat.tsx)
    │  POST /api/v1/chat
    │  {message: str, session_id: str}
    ▼
Backend (api/chat.py)
    │
    └─ QueryAgent (agents/query.py)
          │  session_id → SqliteDb (llm_wiki.db)
          │  add_history_to_context=True
          │  num_history_runs=5
          │
          ├─ tool: list_wiki_pages()
          ├─ tool: search_wiki_pages(query)
          └─ tool: get_wiki_page(slug)
          │
          ▼
    {answer: str, sources: list[str], session_id: str}
```

---

## Backend

### Nuovo: `backend/app/agents/query.py`

Factory `make_query_agent(db, session_id) -> Agent`.

- Provider LLM: `get_llm_model(role="query")` — già esistente in `core/llm.py`
- Session persistence: `SqliteDb(db_file=<path da settings>)` — stesso file `llm_wiki.db`, Agno crea tabella `sessions` autonomamente
- `add_history_to_context=True`, `num_history_runs=5`
- 3 tool async che wrappano query SQLAlchemy sulla sessione DB passata:
  1. `list_wiki_pages()` — SELECT slug, titolo FROM procedure_wiki
  2. `search_wiki_pages(query: str)` — SELECT slug, titolo FROM procedure_wiki WHERE titolo ILIKE %query% OR contenuto_md ILIKE %query% LIMIT 10
  3. `get_wiki_page(slug: str)` — SELECT contenuto_md FROM procedure_wiki WHERE slug = slug

### Nuovo: `backend/app/agents/prompts/query.md`

Prompt italiano. Istruzioni chiave:
- Rispondere solo su informazioni presenti nelle pagine wiki
- Usare `search_wiki_pages` per trovare pagine rilevanti, poi `get_wiki_page` per leggerle
- Chiudere sempre la risposta con `**Fonti:** slug1, slug2` elenco degli slug consultati
- Tono formale italiano
- Non inventare informazioni non presenti nella wiki

### Nuovo: `backend/app/api/chat.py`

Endpoint: `POST /api/v1/chat`

**Request schema:**
```python
class ChatRequest(BaseModel):
    message: str
    session_id: str
```

**Response schema:**
```python
class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    session_id: str
```

Logica:
1. Istanzia `make_query_agent(db, session_id)`
2. Chiama `agent.arun(message)`
3. Estrae le fonti con regex `\*\*Fonti:\*\*\s*(.+)` dall'ultima riga
4. Rimuove la riga Fonti dall'`answer` prima di restituirla
5. Richiede header `X-API-Key` (dependency `verify_api_key` già esistente)

### Modificato: `backend/app/main.py`

Aggiunge:
```python
from app.api.chat import router as chat_router
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
```

---

## Frontend

### Nuovo: `frontend/src/api/chat.ts`

```typescript
sendMessage(message: string, session_id: string): Promise<ChatResponse>
```
Chiama `POST /api/v1/chat` con gli stessi header `X-API-Key` degli altri client.

### Nuovo: `frontend/src/pages/Chat.tsx`

**Session management:**
- `session_id` generato con `crypto.randomUUID()` al primo render
- Salvato in `localStorage` con chiave `wiki_chat_session_id`
- Sopravvive al refresh, consente conversazioni continue

**State:**
```typescript
type Message = {
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
}
const [messages, setMessages] = useState<Message[]>([])
const [input, setInput] = useState('')
const [loading, setLoading] = useState(false)
```

**UX:**
- Bubble di messaggi distinte per utente e assistente
- Sotto ogni risposta assistente: chip cliccabili per ogni fonte
- Click su chip → callback `onNavigateToWiki(slug)` che apre la tab Wiki sulla pagina corrispondente
- Loading: tre puntini animati durante attesa risposta
- Input disabilitato durante loading (previene invii multipli)
- Auto-scroll al messaggio più recente
- Messaggio di benvenuto iniziale che spiega cosa fare

### Modificato: `frontend/src/App.tsx`

- Aggiunge tab "Chat" nella navbar
- Stato `currentPage` esteso a `'procedures' | 'wiki' | 'chat'`
- Quando si clicca un chip fonte nella Chat: `setCurrentPage('wiki')` + passa lo slug selezionato alla pagina Wiki

---

## Flusso dati completo

```
1. Utente apre tab Chat
   └─ frontend legge/genera session_id da localStorage

2. Utente scrive domanda e invia
   └─ POST /api/v1/chat {message, session_id}

3. Backend: make_query_agent(db, session_id)
   └─ Agno carica history sessione da SQLite

4. Agent run:
   ├─ search_wiki_pages(query) → trova pagine rilevanti
   ├─ get_wiki_page(slug) × N → legge contenuti
   └─ Risponde in italiano con **Fonti:** slug1, slug2

5. Backend:
   ├─ Estrae sources dalla risposta
   └─ Restituisce {answer, sources, session_id}

6. Frontend:
   ├─ Aggiunge messaggio assistente alla lista
   └─ Mostra chip fonti cliccabili sotto la risposta
```

---

## Cosa non è incluso in questo scope

- Streaming SSE (può essere aggiunto in futuro)
- Gestione multi-utente (session_id per browser, non per account)
- Cancellazione di una sessione chat (reset manuale del localStorage)
- Indicizzazione vettoriale (non necessaria: `search_wiki_pages` con ILIKE è sufficiente per wiki aziendali di dimensioni normali)
