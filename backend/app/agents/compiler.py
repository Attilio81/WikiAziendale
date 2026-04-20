import uuid
from datetime import datetime, timezone
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.procedure_raw import ProcedureRaw
from app.models.procedure_wiki import ProcedureWiki
from app.models.wiki_index import WikiIndex


def make_compiler_tools(db: AsyncSession, model_id: str) -> tuple[list[Callable], dict]:
    """Return (tools, state). Tools are async closures over db. state tracks affected_slugs."""
    state: dict = {"affected_slugs": []}

    async def get_raw_procedure(procedure_id: str) -> str:
        """Get a raw procedure by its UUID. Returns full text with title, category, content."""
        try:
            pid = uuid.UUID(procedure_id)
        except ValueError:
            return f"Errore: ID non valido '{procedure_id}'"
        proc = await db.get(ProcedureRaw, pid)
        if not proc:
            return f"Errore: procedura '{procedure_id}' non trovata"
        tags = ", ".join(proc.tags or [])
        return (
            f"ID: {proc.id}\n"
            f"Titolo: {proc.titolo}\n"
            f"Categoria: {proc.categoria or 'N/A'}\n"
            f"Autore: {proc.autore or 'N/A'}\n"
            f"Tags: {tags}\n"
            f"Versione: {proc.version}\n\n"
            f"Contenuto:\n{proc.contenuto_md}"
        )

    async def list_wiki_pages() -> str:
        """List all existing wiki pages with slug, title, and source procedure IDs."""
        result = await db.execute(
            select(ProcedureWiki.slug, ProcedureWiki.titolo, ProcedureWiki.source_raw_ids)
        )
        rows = result.all()
        if not rows:
            return "Nessuna pagina wiki esistente."
        lines = [
            f"- slug='{r.slug}' | titolo='{r.titolo}' | fonti={r.source_raw_ids}"
            for r in rows
        ]
        return "Pagine wiki esistenti:\n" + "\n".join(lines)

    async def get_wiki_page(slug: str) -> str:
        """Get full content of a wiki page by slug."""
        result = await db.execute(select(ProcedureWiki).where(ProcedureWiki.slug == slug))
        page = result.scalar_one_or_none()
        if not page:
            return f"Errore: pagina wiki '{slug}' non trovata"
        links_str = ", ".join(page.links or [])
        sources_str = ", ".join(str(s) for s in (page.source_raw_ids or []))
        return (
            f"Slug: {page.slug}\n"
            f"Titolo: {page.titolo}\n"
            f"Links: {links_str}\n"
            f"Fonti raw: {sources_str}\n\n"
            f"Contenuto:\n{page.contenuto_md}"
        )

    async def upsert_wiki_page(
        slug: str,
        titolo: str,
        contenuto_md: str,
        links: list[str],
        source_raw_ids: list[str],
    ) -> str:
        """Create or update a wiki page. slug must be lowercase with hyphens (e.g. 'ricezione-merci')."""
        result = await db.execute(select(ProcedureWiki).where(ProcedureWiki.slug == slug))
        page = result.scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if page:
            page.titolo = titolo
            page.contenuto_md = contenuto_md
            page.links = links
            page.source_raw_ids = source_raw_ids
            page.last_compiled_at = now
            page.compilation_model = model_id
            page.version += 1
            action = "aggiornata"
        else:
            page = ProcedureWiki(
                slug=slug,
                titolo=titolo,
                contenuto_md=contenuto_md,
                links=links,
                source_raw_ids=source_raw_ids,
                last_compiled_at=now,
                compilation_model=model_id,
                version=1,
            )
            db.add(page)
            action = "creata"
        await db.flush()
        state["affected_slugs"].append(slug)
        return f"Pagina wiki '{slug}' {action} con successo."

    async def delete_wiki_page(slug: str) -> str:
        """Delete a wiki page by slug. Use only when a page is no longer relevant."""
        result = await db.execute(select(ProcedureWiki).where(ProcedureWiki.slug == slug))
        page = result.scalar_one_or_none()
        if not page:
            return f"Errore: pagina '{slug}' non trovata"
        await db.delete(page)
        await db.flush()
        return f"Pagina wiki '{slug}' eliminata."

    async def rebuild_wiki_index() -> str:
        """Rebuild the navigable wiki index from all pages. Call this after all upserts are done."""
        result = await db.execute(
            select(ProcedureWiki.slug, ProcedureWiki.titolo).order_by(ProcedureWiki.titolo)
        )
        rows = result.all()
        if not rows:
            tree_md = "# Indice Wiki Aziendale\n\nNessuna pagina disponibile."
        else:
            lines = ["# Indice Wiki Aziendale\n"]
            lines += [f"- [{r.titolo}]({r.slug})" for r in rows]
            tree_md = "\n".join(lines)

        index = await db.get(WikiIndex, 1)
        now = datetime.now(timezone.utc)
        if index:
            index.tree_md = tree_md
            index.last_rebuilt_at = now
        else:
            db.add(WikiIndex(id=1, tree_md=tree_md, last_rebuilt_at=now))
        await db.flush()
        return f"Indice wiki ricostruito con {len(rows)} pagine."

    tools = [
        get_raw_procedure,   # tools[0]
        list_wiki_pages,     # tools[1]
        get_wiki_page,       # tools[2]
        upsert_wiki_page,    # tools[3]
        delete_wiki_page,    # tools[4]
        rebuild_wiki_index,  # tools[5]
    ]
    return tools, state
