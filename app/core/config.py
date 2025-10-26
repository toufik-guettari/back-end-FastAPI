"""Configuration centralisée avec validation Pydantic."""
from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration application avec validation stricte."""
    
    # App metadata
    APP_NAME: str = "FastAPI Industrie Ultra"
    APP_VERSION: str = "1.0.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = Field(default=False, description="Mode debug (logs verbeux)")
    
    # Server
    HOST: str = Field(default="0.0.0.0", description="Host bind address")
    PORT: int = Field(default=8000, ge=1024, le=65535, description="Port bind")
    WORKERS: int = Field(default=1, ge=1, le=16, description="Nombre workers uvicorn")
    
    # Database
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="fastapi_db")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432, ge=1024, le=65535)
    DATABASE_URL: PostgresDsn | None = Field(
        default=None, 
        description="URL complète override (si fournie, prioritaire)"
    )
    DB_POOL_SIZE: int = Field(default=5, ge=1, le=50)
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0, le=50)
    DB_ECHO: bool = Field(default=False, description="Log SQL queries")
    
    # Security
    SECRET_KEY: str = Field(
        default="CHANGE_ME_IN_PRODUCTION_USE_OPENSSL_RAND",
        min_length=32,
        description="Clé secrète pour JWT/sessions"
    )
    ALLOWED_ORIGINS: list[str] = Field(
        default=["http://localhost:3000"],
        description="CORS origins autorisées"
    )
    
    # Observability
    SENTRY_DSN: str | None = Field(default=None, description="Sentry DSN pour error tracking")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=0.1, ge=0.0, le=1.0)
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    
    # Rate limiting (optionnel)
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # ignore vars non définies
    )
    
    @field_validator("APP_ENV")
    @classmethod
    def validate_env(cls, v: str) -> str:
        """Valide que l'environnement est reconnu."""
        if v not in {"development", "staging", "production"}:
            raise ValueError(f"APP_ENV invalide: {v}")
        return v
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key_prod(cls, v: str, info) -> str:
        """En production, SECRET_KEY ne doit pas être la valeur par défaut."""
        if info.data.get("APP_ENV") == "production" and "CHANGE_ME" in v:
            raise ValueError("SECRET_KEY doit être changée en production!")
        return v
    
    @property
    def db_dsn(self) -> str:
        """Construit la DSN PostgreSQL async."""
        if self.DATABASE_URL:
            # Si DATABASE_URL fournie, on l'utilise directement
            url = str(self.DATABASE_URL)
            # S'assurer qu'elle utilise asyncpg
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        
        # Sinon, construire depuis composants
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def is_production(self) -> bool:
        """Helper pour vérifier si on est en production."""
        return self.APP_ENV == "production"
    
    @property
    def is_development(self) -> bool:
        """Helper pour vérifier si on est en développement."""
        return self.APP_ENV == "development"
    
    def __repr__(self) -> str:
        """Représentation sans secrets."""
        return (
            f"Settings(APP_NAME={self.APP_NAME!r}, "
            f"APP_ENV={self.APP_ENV!r}, "
            f"POSTGRES_HOST={self.POSTGRES_HOST!r}, "
            f"DEBUG={self.DEBUG})"
        )


@lru_cache
def get_settings() -> Settings:
    """Factory avec cache pour éviter re-parsing .env à chaque appel."""
    return Settings()


# Instance globale (lazy-loaded via factory)
settings = get_settings()