from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "APIx"
    database_url: str = "sqlite:///./apix.db"
    seed_on_startup: bool = True
    coverage_threshold: float = 0.60
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APIX_")


@lru_cache
def get_settings() -> Settings:
    return Settings()
