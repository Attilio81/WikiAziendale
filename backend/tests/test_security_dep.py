import pytest


def test_security_module_importable():
    from app.core.security import verify_api_key
    import inspect
    assert inspect.iscoroutinefunction(verify_api_key)
