# Wiki Aziendale LLM

> Trasforma procedure aziendali grezze in una wiki strutturata e navigabile, usando un agente AI locale.

![Python](https://img.shields.io/badge/Python-3.11+-3776ab?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61dafb?logo=react&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite-aiosqlite-003b57?logo=sqlite&logoColor=white)
![Agno](https://img.shields.io/badge/AI-Agno_1.4-6366f1)
![License](https://img.shields.io/badge/License-MIT-22c55e)

---

## Cos'è

Un sistema che risolve un problema reale: le procedure aziendali esistono come documenti Word, PDF e appunti sparsi, scritti in momenti diversi da persone diverse. Trovarle e tenerle aggiornate è faticoso.

**Wiki Aziendale LLM** fa questo:

```
Procedura grezza (testo qualsiasi)
        ↓
  Agente AI (Agno + LLM locale)
        ↓
  Pagina wiki strutturata
  con passi, responsabili e link
```

Non è un sistema RAG. La conoscenza viene compilata una volta e servita dal database — nessuna chiamata LLM durante la consultazione.

---

## Funzionalità

- **CRUD procedure** — carica, modifica ed elimina procedure nel formato che hai
- **Compilazione automatica** — l'agente AI crea o aggiorna la pagina wiki appena salvi
- **Fusione intelligente** — se due procedure trattano lo stesso argomento, l'AI le unisce
- **Wiki navigabile** — sidebar con ricerca, pagine in Markdown renderizzato
- **Indice automatico** — struttura ad albero ricostruita ad ogni modifica
- **Multi-provider AI** — LM Studio locale, OpenAI, OpenRouter, Azure OpenAI
- **Tutto in locale** — nessuna dipendenza cloud obbligatoria

---

## Stack

| Layer | Tecnologia |
|---|---|
| Backend | FastAPI 0.115 + Uvicorn, Python 3.11+ |
| AI agent | [Agno](https://agno.ai) 1.4 |
| Database | SQLite + SQLAlchemy asyncio + aiosqlite |
| Schema / Config | Pydantic v2 + pydantic-settings |
| Migrazioni | Alembic |
| Frontend | React 18 + Vite + TypeScript |
| UI | Tailwind CSS 3 |
| State | TanStack Query + Zustand |

---

## Avvio rapido (Windows)

```bat
start.bat
```

Il bat gestisce tutto: installa le dipendenze Python e Node (solo se mancanti), sincronizza il `.env` e avvia i due server in finestre separate.

- **Frontend** → http://localhost:5175
- **Backend API** → http://localhost:8000
- **Docs API interattive** → http://localhost:8000/docs

---

## Setup manuale

### Prerequisiti

- Python 3.11+
- Node.js 20+
- [LM Studio](https://lmstudio.ai) con un modello caricato (o credenziali OpenAI/OpenRouter)

### Backend

```bash
pip install -e "backend[dev]"
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --port 5175
```

### Docker

```bash
cp .env.example .env
docker-compose up --build
```

---

## Configurazione

Copia `.env.example` → `.env` e imposta il provider AI:

```env
# Provider: lmstudio | openai | openrouter | azure
LLM_PROVIDER=lmstudio

# LM Studio (dev locale)
LMSTUDIO_BASE_URL=http://127.0.0.1:1234/v1
LMSTUDIO_MODEL_COMPILER=qwen/qwen3-8b

# API
API_KEY=dev-change-me
API_CORS_ORIGINS=["http://localhost:5175"]
```

| Provider | Variabili richieste | Uso consigliato |
|---|---|---|
| `lmstudio` | `LMSTUDIO_BASE_URL`, `LMSTUDIO_MODEL_*` | Sviluppo locale |
| `openai` | `OPENAI_API_KEY` | Demo / staging |
| `openrouter` | `OPENROUTER_API_KEY` | Produzione cloud |
| `azure` | `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY` | Produzione EU |

> **Nota CORS:** `API_CORS_ORIGINS` richiede un JSON array valido — non una stringa semplice.

---

## Architettura

```
Browser (React SPA : 5175)
         │  REST + X-API-Key
         ▼
Backend FastAPI (: 8000)
         │                    │
         ▼                    ▼
   SQLite DB           Agente Agno
   (llm_wiki.db)       (background task)
                              │
                              ▼
                     LM Studio / OpenAI
                     (porta 1234 / cloud)
```

### Flusso compilazione

```
POST /procedures/
  └─ Salva procedura (status = pending)
  └─ BackgroundTask → compile_in_background()
        └─ Agente AI con 6 tool:
             ├─ get_raw_procedure()
             ├─ list_wiki_pages()
             ├─ get_wiki_page()
             ├─ upsert_wiki_page()    ← scrive la wiki
             ├─ delete_wiki_page()
             └─ rebuild_wiki_index()
        └─ procedure.status = "compiled"
        └─ CompilationLog saved
```

---

## Database

| Tabella | Contenuto |
|---|---|
| `procedure_raw` | Procedure grezze caricate dall'utente |
| `procedure_wiki` | Pagine wiki compilate dall'AI (una per argomento) |
| `wiki_index` | Indice strutturato della wiki (Markdown) |
| `compilation_log` | Log di ogni esecuzione dell'agente |

Le tabelle vengono create automaticamente all'avvio. Per ambienti multi-deploy usare Alembic:

```bash
cd backend
alembic upgrade head
```

---

## Test

```bash
cd backend
pytest tests/ -v   # 25 test
```

---

## Struttura progetto

```
WikiAziendale/
├── .env                    ← config unica (copiata in backend/)
├── start.bat               ← avvio completo Windows
├── docker-compose.yml
├── backend/
│   ├── app/
│   │   ├── api/            ← procedures.py, wiki.py
│   │   ├── agents/         ← compiler.py + prompts/
│   │   ├── services/       ← compilation.py
│   │   ├── models/         ← SQLAlchemy ORM
│   │   ├── schemas/        ← Pydantic v2
│   │   └── core/           ← db, llm factory, security
│   ├── alembic/
│   └── tests/
├── frontend/
│   └── src/
│       ├── api/
│       ├── pages/          ← Procedures, Wiki
│       └── components/
├── docs/
│   ├── manuale-tecnico.html
│   └── manuale-utente.html
└── fixtures/               ← 18 procedure campione
```

---

## Documentazione

| Documento | Audience |
|---|---|
| [Manuale Tecnico](docs/manuale-tecnico.html) | Sviluppatori e sysadmin |
| [Manuale Utente](docs/manuale-utente.html) | Utenti finali |
| [Come Funziona](COME-FUNZIONA.md) | Overview non tecnico |

---

## Roadmap

- [x] Phase 1 — CRUD procedure + frontend gestione
- [x] Phase 2 — Compiler Agent, wiki auto-generate
- [ ] Phase 3 — Query Agent, chat UI
- [ ] Phase 4 — Osservabilità, metriche, deploy guide

---

## Limitazioni note

- `COMPILER_TIMEOUT_SECONDS` configurato ma non ancora applicato all'agente
- `tokens_used` sempre null nel log (Agno non espone usage)
- Eliminare una procedura non aggiorna la wiki (richiede rebuild manuale)
- SQLite: nessuna concorrenza in scrittura (adeguato per uso aziendale small-scale)

---

## Licenza

MIT
