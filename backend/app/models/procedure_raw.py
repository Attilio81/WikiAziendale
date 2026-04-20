import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class ProcedureRaw(Base):
    __tablename__ = "procedure_raw"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    titolo: Mapped[str] = mapped_column(String(300), nullable=False)
    categoria: Mapped[str | None] = mapped_column(String(100))
    contenuto_md: Mapped[str] = mapped_column(Text, nullable=False)
    autore: Mapped[str | None] = mapped_column(String(100))
    tags: Mapped[list | None] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    compilation_status: Mapped[str] = mapped_column(String(20), default="pending")
    compilation_error: Mapped[str | None] = mapped_column(Text)
