from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./llm_wiki.db"
    API_KEY: str = "dev-change-me"
    API_CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    LLM_PROVIDER: str = "lmstudio"

    LMSTUDIO_BASE_URL: str = "http://192.168.44.150:1234/v1"
    LMSTUDIO_MODEL_COMPILER: str = "qwen/qwen3-8b"
    LMSTUDIO_MODEL_QUERY: str = "qwen/qwen3-8b"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_COMPILER: str = "gpt-4o-mini"
    OPENAI_MODEL_QUERY: str = "gpt-4o-mini"

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL_COMPILER: str = "qwen/qwen3-30b-a3b"
    OPENROUTER_MODEL_QUERY: str = "qwen/qwen3-30b-a3b"

    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_DEPLOYMENT_COMPILER: str = "gpt-4o-mini"
    AZURE_OPENAI_DEPLOYMENT_QUERY: str = "gpt-4o-mini"

    COMPILER_TIMEOUT_SECONDS: int = 180
    QUERY_TIMEOUT_SECONDS: int = 30
    COMPILER_MAX_RETRIES: int = 1

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
