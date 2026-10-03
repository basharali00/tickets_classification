import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str
    DEBUG: bool = False
    DATABASE_URL: str
    REDIS_URL: str = "redis://redis:6379/0"
    ANTHROPIC_API_KEY: str | None = None


class LocalConfig(BaseConfig):
    ENVIRONMENT: str = "local"
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql+psycopg://tickets:tickets@postgres:5432/tickets"


class TestConfig(BaseConfig):
    ENVIRONMENT: str = "test"
    DATABASE_URL: str = (
        "postgresql+psycopg://tickets:tickets@postgres:5432/tickets_test"
    )


class ProdConfig(BaseConfig):
    ENVIRONMENT: str = "prod"


CONFIGS: dict[str, type[BaseConfig]] = {
    "local": LocalConfig,
    "test": TestConfig,
    "prod": ProdConfig,
}


def get_settings() -> BaseConfig:
    environment = os.getenv("ENVIRONMENT", "local")
    if environment not in CONFIGS:
        raise ValueError(
            f"ENVIRONMENT must be one of {list(CONFIGS)}, got {environment!r}"
        )

    return CONFIGS[environment]()  # pyright: ignore[reportCallIssue]


settings = get_settings()
