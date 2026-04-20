import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.db import get_db
from app.core.security import verify_api_key
from app.models.compilation_log import CompilationLog
from app.models.procedure_raw import ProcedureRaw
from app.models.procedure_wiki import ProcedureWiki
from app.models.wiki_index import WikiIndex
from app.schemas.wiki import (
    CompilationLogListResponse,
    WikiIndexRead,
    WikiPageListItem,
    WikiPageRead,
)
from app.services.compilation import compile_in_background

router = APIRouter()


@router.get("/index", response_model=WikiIndexRead)
async def get_wiki_index(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    index = await db.get(WikiIndex, 1)
    if not index:
        return WikiIndexRead(id=1, tree_md=None, last_rebuilt_at=None)
    return index


@router.get("/pages", response_model=list[WikiPageListItem])
async def list_wiki_pages(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    result = await db.execute(select(ProcedureWiki).order_by(ProcedureWiki.titolo))
    return list(result.scalars().all())


@router.get("/pages/{slug}", response_model=WikiPageRead)
async def get_wiki_page(
    slug: str,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    result = await db.execute(select(ProcedureWiki).where(ProcedureWiki.slug == slug))
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail=f"Pagina wiki '{slug}' non trovata")
    return page


@router.post("/rebuild", status_code=202)
async def trigger_rebuild(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    result = await db.execute(select(ProcedureRaw.id))
    ids: list[uuid.UUID] = [row[0] for row in result.all()]
    if not ids:
        return {"message": "Nessuna procedura da compilare", "count": 0}
    background_tasks.add_task(compile_in_background, ids, "rebuild")
    return {"message": f"Ricompilazione avviata per {len(ids)} procedure", "count": len(ids)}


@router.get("/compilation-log", response_model=CompilationLogListResponse)
async def list_compilation_log(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    stmt = select(CompilationLog).order_by(CompilationLog.triggered_at.desc())
    total = await db.scalar(select(func.count()).select_from(stmt.subquery()))
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    return CompilationLogListResponse(items=items, total=total or 0, page=page, page_size=page_size)
