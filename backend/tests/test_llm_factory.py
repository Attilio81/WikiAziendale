import os
import pytest
from unittest.mock import patch, MagicMock
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


# ---------------------------------------------------------------------------
# OpenAI branch
# ---------------------------------------------------------------------------

def test_get_llm_model_openai_missing_key_raises():
    with patch.dict(os.environ, {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": ""}, clear=False):
        get_settings.cache_clear()
        from app.core.llm import get_llm_model
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            get_llm_model("compiler")


def test_get_llm_model_openai_returns_instance():
    fake_key = "sk-test-openai"
    mock_instance = MagicMock()
    with patch.dict(os.environ, {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": fake_key}, clear=False):
        get_settings.cache_clear()
        from app.core.llm import get_llm_model
        with patch("agno.models.openai.OpenAIChat", return_value=mock_instance) as mock_cls:
            result = get_llm_model("compiler")
            mock_cls.assert_called_once()
            assert result is mock_instance


def test_get_llm_model_openai_query_role():
    fake_key = "sk-test-openai"
    mock_instance = MagicMock()
    with patch.dict(
        os.environ,
        {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": fake_key, "OPENAI_MODEL_QUERY": "gpt-4o"},
        clear=False,
    ):
        get_settings.cache_clear()
        from app.core.llm import get_llm_model
        with patch("agno.models.openai.OpenAIChat", return_value=mock_instance) as mock_cls:
            result = get_llm_model("query")
            call_kwargs = mock_cls.call_args
            assert call_kwargs.kwargs.get("id") == "gpt-4o" or call_kwargs.args[0] == "gpt-4o" or (
                # id may be passed as positional or keyword
                "gpt-4o" in str(call_kwargs)
            )
            assert result is mock_instance


# ---------------------------------------------------------------------------
# OpenRouter branch
# ---------------------------------------------------------------------------

def test_get_llm_model_openrouter_missing_key_raises():
    with patch.dict(os.environ, {"LLM_PROVIDER": "openrouter", "OPENROUTER_API_KEY": ""}, clear=False):
        get_settings.cache_clear()
        from app.core.llm import get_llm_model
        with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
            get_llm_model("compiler")


def test_get_llm_model_openrouter_returns_instance():
    fake_key = "or-test-key"
    mock_instance = MagicMock()
    with patch.dict(os.environ, {"LLM_PROVIDER": "openrouter", "OPENROUTER_API_KEY": fake_key}, clear=False):
        get_settings.cache_clear()
        from app.core.llm import get_llm_model
        with patch("agno.models.openrouter.OpenRouter", return_value=mock_instance) as mock_cls:
            result = get_llm_model("compiler")
            mock_cls.assert_called_once()
            assert result is mock_instance


# ---------------------------------------------------------------------------
# Azure branch
# ---------------------------------------------------------------------------

def test_get_llm_model_azure_missing_key_raises():
    with patch.dict(
        os.environ,
        {"LLM_PROVIDER": "azure", "AZURE_OPENAI_API_KEY": "", "AZURE_OPENAI_ENDPOINT": "https://x.openai.azure.com"},
        clear=False,
    ):
        get_settings.cache_clear()
        from app.core.llm import get_llm_model
        with pytest.raises(ValueError, match="AZURE_OPENAI_API_KEY"):
            get_llm_model("compiler")


def test_get_llm_model_azure_missing_endpoint_raises():
    with patch.dict(
        os.environ,
        {"LLM_PROVIDER": "azure", "AZURE_OPENAI_API_KEY": "az-test-key", "AZURE_OPENAI_ENDPOINT": ""},
        clear=False,
    ):
        get_settings.cache_clear()
        from app.core.llm import get_llm_model
        with pytest.raises(ValueError, match="AZURE_OPENAI_ENDPOINT"):
            get_llm_model("compiler")


def test_get_llm_model_azure_returns_instance():
    fake_key = "az-test-key"
    fake_endpoint = "https://my-resource.openai.azure.com"
    mock_instance = MagicMock()
    with patch.dict(
        os.environ,
        {"LLM_PROVIDER": "azure", "AZURE_OPENAI_API_KEY": fake_key, "AZURE_OPENAI_ENDPOINT": fake_endpoint},
        clear=False,
    ):
        get_settings.cache_clear()
        from app.core.llm import get_llm_model
        with patch("agno.models.azure.AzureOpenAI", return_value=mock_instance) as mock_cls:
            result = get_llm_model("compiler")
            mock_cls.assert_called_once()
            assert result is mock_instance
