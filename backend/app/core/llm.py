from typing import Literal
from app.config import get_settings


def get_llm_model(role: Literal["compiler", "query"] = "compiler"):
    """Return an Agno model instance based on LLM_PROVIDER setting."""
    s = get_settings()
    provider = s.LLM_PROVIDER
    timeout = float(s.COMPILER_TIMEOUT_SECONDS if role == "compiler" else s.QUERY_TIMEOUT_SECONDS)

    if provider == "lmstudio":
        from agno.models.lmstudio import LMStudio
        model_id = s.LMSTUDIO_MODEL_COMPILER if role == "compiler" else s.LMSTUDIO_MODEL_QUERY
        return LMStudio(id=model_id, base_url=s.LMSTUDIO_BASE_URL, timeout=timeout)

    if provider == "openai":
        from agno.models.openai import OpenAIChat
        if not s.OPENAI_API_KEY:
            raise ValueError("LLM_PROVIDER=openai requires OPENAI_API_KEY to be set")
        model_id = s.OPENAI_MODEL_COMPILER if role == "compiler" else s.OPENAI_MODEL_QUERY
        return OpenAIChat(id=model_id, api_key=s.OPENAI_API_KEY, timeout=timeout)

    if provider == "openrouter":
        from agno.models.openrouter import OpenRouter
        if not s.OPENROUTER_API_KEY:
            raise ValueError("LLM_PROVIDER=openrouter requires OPENROUTER_API_KEY to be set")
        model_id = s.OPENROUTER_MODEL_COMPILER if role == "compiler" else s.OPENROUTER_MODEL_QUERY
        return OpenRouter(id=model_id, api_key=s.OPENROUTER_API_KEY, timeout=timeout)

    if provider == "azure":
        from agno.models.azure import AzureOpenAI
        if not s.AZURE_OPENAI_API_KEY:
            raise ValueError("LLM_PROVIDER=azure requires AZURE_OPENAI_API_KEY to be set")
        if not s.AZURE_OPENAI_ENDPOINT:
            raise ValueError("LLM_PROVIDER=azure requires AZURE_OPENAI_ENDPOINT to be set")
        model_id = s.AZURE_OPENAI_DEPLOYMENT_COMPILER if role == "compiler" else s.AZURE_OPENAI_DEPLOYMENT_QUERY
        return AzureOpenAI(
            id=model_id,
            api_key=s.AZURE_OPENAI_API_KEY,
            azure_endpoint=s.AZURE_OPENAI_ENDPOINT,
            timeout=timeout,
        )

    raise ValueError(f"Unknown LLM_PROVIDER: {provider!r}. Valid: lmstudio, openai, openrouter, azure")
