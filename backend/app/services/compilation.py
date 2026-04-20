import time
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.compiler import make_compiler_agent, _get_compiler_model_id
from app.config import get_settings
from app.models.procedure_raw import ProcedureRaw
from app.models.compilation_log import CompilationLog


async def run_compilation(
    procedure_ids: list[uuid.UUID],
    trigger_type: str,
    db: AsyncSession,
) -> CompilationLog:
    """Run compiler agent. Updates procedure statuses and writes CompilationLog. Commits on finish."""
    settings = get_settings()
    triggered_at = datetime.now(timezone.utc)
    t0 = time.monotonic()

    agent, state = make_compiler_agent(db)

    ids_str = ", ".join(str(pid) for pid in procedure_ids)
    if trigger_type == "rebuild":
        msg = (
            f"Ricompila tutte le procedure con ID: {ids_str}. "
            "Per ognuna leggi la procedura, aggiorna o crea la pagina wiki appropriata. "
            "Al termine chiama rebuild_wiki_index."
        )
    else:
        msg = (
            f"Compila la procedura con ID: {ids_str}. "
            "Leggi la procedura, consulta le pagine wiki esistenti, "
            "aggiorna o crea la pagina wiki appropriata. "
            "Al termine chiama rebuild_wiki_index."
        )

    try:
        await agent.arun(msg)

        for pid in procedure_ids:
            proc = await db.get(ProcedureRaw, pid)
            if proc:
                proc.compilation_status = "compiled"
                proc.compilation_error = None

        duration_ms = int((time.monotonic() - t0) * 1000)
        log = CompilationLog(
            triggered_at=triggered_at,
            trigger_type=trigger_type,
            affected_raw_ids=[str(pid) for pid in procedure_ids],
            affected_wiki_slugs=list(state["affected_slugs"]),
            duration_ms=duration_ms,
            model_used=_get_compiler_model_id(settings),
            status="completed",
        )
        db.add(log)
        await db.commit()
        return log

    except Exception as exc:
        await db.rollback()
        err = str(exc)[:2000]
        duration_ms = int((time.monotonic() - t0) * 1000)

        for pid in procedure_ids:
            proc = await db.get(ProcedureRaw, pid)
            if proc:
                proc.compilation_status = "failed"
                proc.compilation_error = err

        log = CompilationLog(
            triggered_at=triggered_at,
            trigger_type=trigger_type,
            affected_raw_ids=[str(pid) for pid in procedure_ids],
            affected_wiki_slugs=[],
            duration_ms=duration_ms,
            model_used=_get_compiler_model_id(settings),
            status="failed",
            error=err,
        )
        db.add(log)
        await db.commit()
        return log


async def compile_in_background(procedure_ids: list[uuid.UUID], trigger_type: str) -> None:
    """Entry point for FastAPI BackgroundTasks. Creates its own DB session."""
    from app.core.db import get_session_factory
    async with get_session_factory()() as db:
        await run_compilation(procedure_ids, trigger_type, db)
