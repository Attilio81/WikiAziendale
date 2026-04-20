def test_all_models_importable():
    from app.models import ProcedureRaw, ProcedureWiki, WikiIndex, CompilationLog
    assert ProcedureRaw.__tablename__ == "procedure_raw"
    assert ProcedureWiki.__tablename__ == "procedure_wiki"
    assert WikiIndex.__tablename__ == "wiki_index"
    assert CompilationLog.__tablename__ == "compilation_log"
