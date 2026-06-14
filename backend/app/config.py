"""PenguWave backend configuration — loaded from .env with sensible defaults."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App settings, pulled from .env or environment variables."""

    database_url: str = "sqlite:///./penguwave.db"
    cors_origin: str = "http://localhost:5173"

    admin_password: str = "admin123"
    analyst_password: str = "pass456"
    viewer_password: str = "view789"

    app_secret: str = "dev-secret-change-in-prod"

    # Claude API key for the AI SOC-analyst triage endpoint. Empty by default so
    # the app boots without it; the triage route returns 503 when it's unset.
    anthropic_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
