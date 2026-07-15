from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    rate_limit_enabled: bool = True
    cache_enabled: bool = True
    redis_url: str = ""
    log_level: str = "INFO"
    allowed_origins: str = "*"
    api_key: str = ""
    default_provider: str = "openai"
    workspace_dir: str = "."
    agent_max_iterations: int = 5
    session_ttl: int = 3600


settings = Settings()
