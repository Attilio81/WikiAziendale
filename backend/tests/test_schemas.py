import pytest
from pydantic import ValidationError


def test_procedure_create_requires_titolo():
    from app.schemas.procedure import ProcedureCreate
    with pytest.raises(ValidationError):
        ProcedureCreate(contenuto_md="x")


def test_procedure_create_empty_titolo_fails():
    from app.schemas.procedure import ProcedureCreate
    with pytest.raises(ValidationError):
        ProcedureCreate(titolo="", contenuto_md="x")


def test_procedure_create_defaults():
    from app.schemas.procedure import ProcedureCreate
    p = ProcedureCreate(titolo="Test", contenuto_md="contenuto")
    assert p.tags == []
    assert p.categoria is None
    assert p.autore is None


def test_procedure_update_all_optional():
    from app.schemas.procedure import ProcedureUpdate
    p = ProcedureUpdate()
    assert p.titolo is None
    assert p.contenuto_md is None
    assert p.tags is None


def test_procedure_read_from_attributes():
    from app.schemas.procedure import ProcedureRead
    import uuid
    from datetime import datetime, timezone
    data = {
        "id": uuid.uuid4(),
        "titolo": "Test",
        "categoria": None,
        "contenuto_md": "content",
        "autore": None,
        "tags": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "version": 1,
        "compilation_status": "pending",
        "compilation_error": None,
    }
    p = ProcedureRead(**data)
    assert p.titolo == "Test"


def test_procedure_list_response():
    from app.schemas.procedure import ProcedureListResponse
    resp = ProcedureListResponse(items=[], total=0, page=1, page_size=20)
    assert resp.total == 0
