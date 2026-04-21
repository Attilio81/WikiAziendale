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
