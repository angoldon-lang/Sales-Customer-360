import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Customer Intelligence Monitor"
    version: str = "0.1.0"
    debug: bool = os.getenv("DEBUG", "False") == "True"

    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./customer_intelligence.db"
    )

    # Email configuration
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from_email: str = os.getenv("SMTP_FROM_EMAIL", "noreply@customer-intelligence.local")

    # News search configuration (abstract, can be mocked)
    news_search_provider: str = os.getenv("NEWS_SEARCH_PROVIDER", "mock")  # mock, bing, serp
    news_search_api_key: str = os.getenv("NEWS_SEARCH_API_KEY", "")

    # AI classification (abstract)
    ai_provider: str = os.getenv("AI_PROVIDER", "mock")  # mock, claude, openai
    ai_api_key: str = os.getenv("AI_API_KEY", "")

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
