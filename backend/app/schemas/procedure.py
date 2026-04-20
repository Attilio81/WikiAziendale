import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProcedureCreate(BaseModel):
    titolo: str = Field(..., min_length=1, max_length=300)
    categoria: Optional[str] = Field(None, max_length=100)
    contenuto_md: str = Field(..., min_length=1)
    autore: Optional[str] = Field(None, max_length=100)
    tags: list[str] = Field(default_factory=list)


class ProcedureUpdate(BaseModel):
    titolo: Optional[str] = Field(None, min_length=1, max_length=300)
    categoria: Optional[str] = Field(None, max_length=100)
    contenuto_md: Optional[str] = Field(None, min_length=1)
    autore: Optional[str] = Field(None, max_length=100)
    tags: Optional[list[str]] = None


class ProcedureRead(BaseModel):
    id: uuid.UUID
    titolo: str
    categoria: Optional[str]
    contenuto_md: str
    autore: Optional[str]
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    version: int
    compilation_status: str
    compilation_error: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class ProcedureListResponse(BaseModel):
    items: list[ProcedureRead]
    total: int
    page: int
    page_size: int
