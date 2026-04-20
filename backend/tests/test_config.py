import os
import pytest


def test_settings_have_correct_defaults():
    os.environ.setdefault("API_KEY", "test-key")
    from app.config import get_settings
    s = get_settings()
    assert "sqlite" in s.DATABASE_URL
    assert s.LLM_PROVIDER == "lmstudio"
    assert s.COMPILER_TIMEOUT_SECONDS == 180


def test_settings_api_key_readable():
    os.environ["API_KEY"] = "test-key-123"
    from app.config import get_settings
    get_settings.cache_clear()
    s = get_settings()
    assert s.API_KEY == "test-key-123"
    get_settings.cache_clear()
