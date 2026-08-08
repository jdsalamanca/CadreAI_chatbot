from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ".env" is resolved relative to the process's working directory (repo root
    # for local runs). In Docker no .env file is shipped; real env vars passed
    # via `docker run -e` / `--env-file` are used instead and take precedence.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openrouter_api_key: str
    openrouter_model: str = "openai/gpt-4o-mini"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    cors_origins: list[str] = ["http://localhost:5173"]
    llm_timeout_seconds: float = 30.0


settings = Settings()
