import os
import pytest
from unittest.mock import patch
from app.config import get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_get_llm_model_lmstudio_returns_lmstudio_instance():
    with patch.dict(os.environ, {"LLM_PROVIDER": "lmstudio"}, clear=False):
        get_settings.cache_clear()
        from app.core.llm import get_llm_model
        from agno.models.lmstudio import LMStudio
        model = get_llm_model("compiler")
        assert isinstance(model, LMStudio)


def test_get_llm_model_unknown_provider_raises():
    with patch.dict(os.environ, {"LLM_PROVIDER": "unknown_xyz"}, clear=False):
        get_settings.cache_clear()
        from app.core.llm import get_llm_model
        with pytest.raises(ValueError, match="Unknown LLM_PROVIDER"):
            get_llm_model("compiler")


def test_get_llm_model_query_role_uses_query_model():
    with patch.dict(os.environ, {"LLM_PROVIDER": "lmstudio", "LMSTUDIO_MODEL_QUERY": "qwen3-4b"}, clear=False):
        get_settings.cache_clear()
        from app.core.llm import get_llm_model
        from agno.models.lmstudio import LMStudio
        model = get_llm_model("query")
        assert isinstance(model, LMStudio)
        assert model.id == "qwen3-4b"
