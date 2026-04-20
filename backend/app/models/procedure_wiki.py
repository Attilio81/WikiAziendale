import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class ProcedureWiki(Base):
    __tablename__ = "procedure_wiki"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    titolo: Mapped[str] = mapped_column(String(300), nullable=False)
    contenuto_md: Mapped[str] = mapped_column(Text, nullable=False)
    links: Mapped[list | None] = mapped_column(JSON, default=list)
    source_raw_ids: Mapped[list | None] = mapped_column(JSON, default=list)
    last_compiled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    compilation_model: Mapped[str | None] = mapped_column(String(100))
    version: Mapped[int] = mapped_column(Integer, default=1)
