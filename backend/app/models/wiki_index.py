from datetime import datetime
from sqlalchemy import Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class WikiIndex(Base):
    __tablename__ = "wiki_index"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    tree_md: Mapped[str | None] = mapped_column(Text)
    last_rebuilt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
