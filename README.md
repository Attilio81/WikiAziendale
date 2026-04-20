# Wiki Aziendale LLM

Sistema di gestione e interrogazione di procedure operative aziendali basato su LLM.

## Requisiti

- Docker + Docker Compose
- Python 3.11+ (sviluppo backend locale)
- Node.js 20+ (sviluppo frontend locale)

## Avvio rapido (Docker)

```bash
cp .env.example .env
docker-compose up --build
```

- Backend API: http://localhost:8000
- Docs API interattive: http://localhost:8000/docs
- Frontend: http://localhost:5173

## Sviluppo locale

### Backend

```bash
cd backend
python -m venv .venv

# Mac/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -e ".[dev]"
cp ../.env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Test backend

```bash
cd backend
pytest tests/ -v
```

### Migrations (Alembic)

```bash
cd backend
# Genera nuova migration dopo modifica modelli
alembic revision --autogenerate -m "descrizione"
# Applica migrations
alembic upgrade head
```

## Configurazione LLM Provider

Impostare `LLM_PROVIDER` nel file `.env`:

| Provider | Caso d'uso | Variabili richieste |
|---|---|---|
| `lmstudio` | Dev locale (LM Studio) | `LMSTUDIO_BASE_URL`, `LMSTUDIO_MODEL_*` |
| `openai` | Staging / demo | `OPENAI_API_KEY` |
| `openrouter` | Produzione cloud | `OPENROUTER_API_KEY` |
| `azure` | Produzione EU data residency | `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY` |

**Setup LM Studio (dev):**
1. Avviare LM Studio e caricare il modello (consigliato: `qwen3-8b` su hardware con 8GB+ RAM)
2. Avviare il server locale (porta 1234 di default)
3. Nel `.env`: `LMSTUDIO_BASE_URL=http://<ip-lmstudio>:1234/v1`

## Struttura progetto

```
llm-wiki/
├── backend/           # FastAPI + SQLAlchemy + Agno agents
│   ├── app/
│   │   ├── api/       # Endpoints REST
│   │   ├── core/      # DB, security, LLM factory
│   │   ├── models/    # SQLAlchemy models (4 tabelle)
│   │   ├── schemas/   # Pydantic v2 schemas
│   │   ├── agents/    # Compiler e Query agent (Phase 2)
│   │   └── services/  # Orchestrazione async (Phase 2)
│   ├── alembic/       # Migrations
│   └── tests/         # 25 test pytest
├── frontend/          # React 18 + Vite + TypeScript
│   └── src/
│       ├── api/       # Client API tipizzato
│       ├── components/ # StatusBadge, ProcedureTable, ProcedureModal
│       ├── pages/     # Procedures (Phase 1), Wiki, Chat (Phase 2+)
│       └── store/     # Zustand modal store
├── fixtures/          # 18 procedure campione per test
├── docker-compose.yml
└── .env.example
```

## Fasi di sviluppo

- **Phase 1** (questo branch): CRUD procedure raw, frontend gestione
- **Phase 2**: Compiler Agent LLM, wiki pages auto-generate
- **Phase 3**: Query Agent, wiki browser, chat UI
- **Phase 4**: Osservabilità, metriche, documentazione deploy
