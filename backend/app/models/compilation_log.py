import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class CompilationLog(Base):
    __tablename__ = "compilation_log"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    trigger_type: Mapped[str] = mapped_column(String(20))
    affected_raw_ids: Mapped[list | None] = mapped_column(JSON, default=list)
    affected_wiki_slugs: Mapped[list | None] = mapped_column(JSON, default=list)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    tokens_used: Mapped[int | None] = mapped_column(Integer)
    model_used: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20))
    error: Mapped[str | None] = mapped_column(Text)
