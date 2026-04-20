import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class WikiPageListItem(BaseModel):
    id: uuid.UUID
    slug: str
    titolo: str
    last_compiled_at: Optional[datetime]
    compilation_model: Optional[str]
    version: int
    source_raw_ids: Optional[list]

    model_config = ConfigDict(from_attributes=True)


class WikiPageRead(BaseModel):
    id: uuid.UUID
    slug: str
    titolo: str
    contenuto_md: str
    links: Optional[list]
    source_raw_ids: Optional[list]
    last_compiled_at: Optional[datetime]
    compilation_model: Optional[str]
    version: int

    model_config = ConfigDict(from_attributes=True)


class WikiIndexRead(BaseModel):
    id: int
    tree_md: Optional[str]
    last_rebuilt_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class CompilationLogRead(BaseModel):
    id: uuid.UUID
    triggered_at: datetime
    trigger_type: str
    affected_raw_ids: Optional[list]
    affected_wiki_slugs: Optional[list]
    duration_ms: Optional[int]
    tokens_used: Optional[int]
    model_used: Optional[str]
    status: str
    error: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class CompilationLogListResponse(BaseModel):
    items: list[CompilationLogRead]
    total: int
    page: int
    page_size: int
