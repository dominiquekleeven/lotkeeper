from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from lotkeeper.common.file_util import find_project_root

PROJECT_ROOT = find_project_root()


@dataclass
class DirectoryConstants:
    LOT_WEB_BUNDLE_DIR: Path = PROJECT_ROOT / "data/web/dist"


class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class AppEnvironment(BaseSettings):
    """Application environment settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- Agent ---
    LOT_AGENT_TOKEN: str = "1234567890"

    # --- Environment ---
    LOT_ENVIRONMENT: Environment = Environment.DEVELOPMENT

    # --- CORS ---
    LOT_ALLOWED_ORIGINS: list[str] = ["*"]

    # --- Database ---
    LOT_POSTGRES_HOST: str = "localhost"
    LOT_POSTGRES_PORT: int = 5432
    LOT_POSTGRES_USER: str = "postgres"
    LOT_POSTGRES_PASSWORD: str = "postgres"
    LOT_POSTGRES_DB: str = "lotkeeper"

    # --- Redis ---
    LOT_VALKEY_HOST: str = "localhost"
    LOT_VALKEY_PORT: int = 6379

    # --- Debug ---
    LOT_DB_ECHO: bool = False

    def is_dev(self) -> bool:
        """Is development environment"""

        return self.LOT_ENVIRONMENT == Environment.DEVELOPMENT

    def is_prod(self) -> bool:
        """Is production environment"""

        return self.LOT_ENVIRONMENT == Environment.PRODUCTION

    def get_database_url(self) -> str:
        """Get the postgres database URL"""

        return f"postgresql+asyncpg://{self.LOT_POSTGRES_USER}:{self.LOT_POSTGRES_PASSWORD}@{self.LOT_POSTGRES_HOST}:{self.LOT_POSTGRES_PORT}/{self.LOT_POSTGRES_DB}"

    def get_database_url_sync(self) -> str:
        """Get the postgres database URL"""

        return f"postgresql+psycopg2://{self.LOT_POSTGRES_USER}:{self.LOT_POSTGRES_PASSWORD}@{self.LOT_POSTGRES_HOST}:{self.LOT_POSTGRES_PORT}/{self.LOT_POSTGRES_DB}"


ENV = AppEnvironment()
DIRS = DirectoryConstants()
