from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.db import get_engine, Base
import app.models  # noqa: F401 — registers all models with Base.metadata
from app.api.procedures import router as procedures_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="LLM Wiki API", version="0.1.0", lifespan=lifespan)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.API_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(procedures_router, prefix="/api/v1/procedures", tags=["procedures"])


@app.get("/health")
async def health():
    return {"status": "ok", "llm_provider": settings.LLM_PROVIDER}
