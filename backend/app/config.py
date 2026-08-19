import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Sales Customer 360"
    version: str = "0.1.0"
    debug: bool = os.getenv("DEBUG", "False") == "True"

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/sales_customer_360"
    )

    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
