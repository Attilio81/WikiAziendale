import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.db import get_db
from app.core.security import verify_api_key
from app.models.procedure_raw import ProcedureRaw
from app.schemas.procedure import (
    ProcedureCreate,
    ProcedureUpdate,
    ProcedureRead,
    ProcedureListResponse,
)

router = APIRouter()


@router.post("/", response_model=ProcedureRead, status_code=status.HTTP_201_CREATED)
async def create_procedure(
    body: ProcedureCreate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    proc = ProcedureRaw(**body.model_dump())
    db.add(proc)
    await db.commit()
    await db.refresh(proc)
    return proc


@router.get("/", response_model=ProcedureListResponse)
async def list_procedures(
    q: str | None = Query(None, description="Ricerca testuale nel titolo"),
    categoria: str | None = None,
    compilation_status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    stmt = select(ProcedureRaw)
    if q:
        stmt = stmt.where(ProcedureRaw.titolo.ilike(f"%{q}%"))
    if categoria:
        stmt = stmt.where(ProcedureRaw.categoria == categoria)
    if compilation_status:
        stmt = stmt.where(ProcedureRaw.compilation_status == compilation_status)
    stmt = stmt.order_by(ProcedureRaw.updated_at.desc())

    total = await db.scalar(select(func.count()).select_from(stmt.subquery()))

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return ProcedureListResponse(items=items, total=total or 0, page=page, page_size=page_size)


@router.get("/{id}", response_model=ProcedureRead)
async def get_procedure(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    proc = await db.get(ProcedureRaw, id)
    if not proc:
        raise HTTPException(status_code=404, detail="Procedura non trovata")
    return proc


@router.put("/{id}", response_model=ProcedureRead)
async def update_procedure(
    id: uuid.UUID,
    body: ProcedureUpdate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    proc = await db.get(ProcedureRaw, id)
    if not proc:
        raise HTTPException(status_code=404, detail="Procedura non trovata")

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(proc, key, value)
    proc.version += 1
    proc.compilation_status = "pending"
    proc.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(proc)
    return proc


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_procedure(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    proc = await db.get(ProcedureRaw, id)
    if not proc:
        raise HTTPException(status_code=404, detail="Procedura non trovata")
    await db.delete(proc)
    await db.commit()
