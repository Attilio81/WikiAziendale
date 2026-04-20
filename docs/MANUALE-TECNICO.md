# Manuale Tecnico — LLM Wiki Aziendale

## Cos'è questo sistema

Un'applicazione web che trasforma procedure aziendali grezze in una wiki navigabile, usando un agente AI per la compilazione automatica. Non è un sistema di ricerca (RAG): la conoscenza è strutturata in pagine collegate, come Wikipedia.

---

## Architettura a volo d'uccello

```
Browser (React)
      │
      ▼
Backend (FastAPI + Python)
      │
      ├── Database SQLite  (procedure grezze + pagine wiki + log)
      └── LM Studio        (AI locale, API compatibile OpenAI)
```

Tutto gira in locale. Non serve internet salvo per scaricare i modelli AI la prima volta.

---

## Componenti principali

### 1. Frontend — `frontend/`

Applicazione React a pagina singola con due sezioni:

| Sezione | Cosa fa |
|---------|---------|
| **Procedure** | CRUD delle procedure grezze: crea, modifica, elimina |
| **Wiki** | Visualizza le pagine wiki compilate dall'AI |

**Stack:** React 18, TypeScript, Vite, Tailwind CSS, React Query, react-markdown

**File chiave:**
```
frontend/src/
├── api/
│   ├── client.ts       ← Base URL, headers, handleResponse (condivisi)
│   ├── procedures.ts   ← CRUD procedure
│   └── wiki.ts         ← Lettura pagine wiki e indice
├── pages/
│   ├── Procedures.tsx  ← Pagina gestione procedure
│   └── Wiki.tsx        ← Browser wiki (sidebar + viewer markdown)
└── App.tsx             ← Navbar + routing a stato (procedures | wiki)
```

---

### 2. Backend — `backend/`

API REST costruita con FastAPI. Gestisce due flussi principali:

**Flusso 1 — Gestione procedure:**
```
POST /api/v1/procedures/
      │
      ├── Salva nel DB (tabella procedure_raw)
      └── Avvia compilazione in background
```

**Flusso 2 — Compilazione wiki (background):**
```
compile_in_background()
      │
      └── run_compilation()
            │
            ├── make_compiler_agent()     ← crea agente Agno con 6 tool
            ├── agent.arun(msg)           ← l'AI legge procedure e scrive wiki
            └── Salva log in DB
```

**File chiave:**
```
backend/app/
├── api/
│   ├── procedures.py   ← CRUD + trigger compilazione
│   └── wiki.py         ← Lettura wiki, rebuild, log compilazione
├── agents/
│   ├── compiler.py     ← Agente AI + 6 tool DB-aware
│   └── prompts/
│       └── compiler.md ← Istruzioni italiane per l'AI
├── services/
│   └── compilation.py  ← Orchestrazione compilazione + error handling
├── models/             ← ORM SQLAlchemy (tabelle DB)
├── schemas/            ← Pydantic (validazione I/O API)
├── core/
│   ├── db.py           ← Sessioni SQLAlchemy async
│   ├── llm.py          ← Factory provider AI (LM Studio / OpenAI / ecc.)
│   └── security.py     ← Verifica X-API-Key
└── config.py           ← Tutte le variabili d'ambiente
```

---

### 3. Database — SQLite

Quattro tabelle principali:

| Tabella | Contenuto |
|---------|-----------|
| `procedure_raw` | Le procedure grezze caricate dall'utente |
| `procedure_wiki` | Le pagine wiki compilate dall'AI (una per argomento) |
| `wiki_index` | L'indice della wiki (struttura ad albero in Markdown) |
| `compilation_log` | Log di ogni esecuzione dell'agente AI |

Il file DB (`llm_wiki.db`) si trova nella cartella `backend/` in sviluppo locale.

---

### 4. Agente AI — il cuore del sistema

L'agente (basato su [Agno](https://agno.ai)) riceve le procedure grezze e ha accesso a 6 tool per operare sul database:

| Tool | Cosa fa |
|------|---------|
| `get_raw_procedure(id)` | Legge una procedura grezza dal DB |
| `list_wiki_pages()` | Elenca le pagine wiki esistenti |
| `get_wiki_page(slug)` | Legge il contenuto di una pagina wiki |
| `upsert_wiki_page(slug, titolo, contenuto)` | Crea o aggiorna una pagina wiki |
| `delete_wiki_page(slug)` | Elimina una pagina wiki |
| `rebuild_wiki_index()` | Ricostruisce l'indice della wiki |

L'AI decide autonomamente se creare una nuova pagina o fondere la procedura in una pagina esistente.

---

### 5. Provider AI

Configurabile via variabile d'ambiente `LLM_PROVIDER`:

| Valore | Provider | Uso consigliato |
|--------|----------|-----------------|
| `lmstudio` | LM Studio (locale) | Sviluppo |
| `openai` | OpenAI API | Demo / staging |
| `openrouter` | OpenRouter | Produzione opzione A |
| `azure` | Azure OpenAI | Produzione (data residency EU) |

---

## Come avviare

```
start.bat
```

Apre due finestre terminale:
- **Backend:** `uvicorn app.main:app --reload` su porta `8000`
- **Frontend:** `npm run dev` su porta `5175`

API interattiva: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Variabili d'ambiente

Tutto in `.env` nella root del progetto (copiato automaticamente in `backend/.env` da `start.bat`).

Le variabili più importanti:

```env
LLM_PROVIDER=lmstudio
LMSTUDIO_BASE_URL=http://192.168.44.150:1234/v1
LMSTUDIO_MODEL_COMPILER=qwen/qwen3-8b
API_KEY=dev-change-me
API_CORS_ORIGINS=["http://localhost:5175"]
```

---

## Flusso dati completo

```
1. Utente carica una procedura grezza (POST /procedures/)
         │
2. Backend salva nel DB con status = "pending"
         │
3. Background task avvia la compilazione
         │
4. Agente AI legge la procedura con get_raw_procedure()
         │
5. Agente controlla le pagine esistenti con list_wiki_pages()
         │
6. Agente decide: nuova pagina o aggiornamento?
         │
7. Agente chiama upsert_wiki_page() con il contenuto strutturato
         │
8. Agente chiama rebuild_wiki_index()
         │
9. Backend aggiorna status procedura → "compiled"
         │
10. Backend scrive log in compilation_log
         │
11. Frontend legge la pagina wiki da GET /wiki/pages/{slug}
```

---

## Punti di estensione noti

- **Timeout agente:** `COMPILER_TIMEOUT_SECONDS` è in config ma non ancora applicato all'agent
- **Token usati:** campo `tokens_used` nel log sempre null (Agno non lo espone ancora)
- **Eliminazione procedura:** non attiva pulizia della wiki né rebuild indice

---

## Migrations DB

Gestite con Alembic. In sviluppo, le tabelle vengono create automaticamente all'avvio se non esistono.

```bash
cd backend
alembic upgrade head   # applica migrazioni pendenti
```
