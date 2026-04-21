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
    if settings.LLM_DISABLE_THINKING:
        system_prompt = "/no_think\n\n" + system_prompt

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
