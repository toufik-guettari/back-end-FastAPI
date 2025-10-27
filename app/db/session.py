"""Configuration de la session SQLAlchemy async."""
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.logger import logger


# Engine global (créé une seule fois)
def create_engine() -> AsyncEngine:
    """Factory pour créer l'engine avec configuration."""
    return create_async_engine(
        settings.db_dsn,
        echo=settings.DB_ECHO,  # Log SQL queries si True
        future=True,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=True,  # Vérifie connexion avant utilisation
        pool_recycle=3600,  # Recycle connexions après 1h
        connect_args={
            "server_settings": {
                "application_name": settings.APP_NAME,
                "jit": "off",  # Performance optimisation
            },
            "command_timeout": 60,
            "timeout": 10,
        },
    )


engine: AsyncEngine = create_engine()

# SessionMaker async
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Évite lazy-load après commit
    autoflush=False,  # Contrôle manuel du flush
    autocommit=False,  # Transactions explicites
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency pour injecter une session DB dans les routes.
    
    Usage:
        @router.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


# Type alias pour dependency injection
DBSession = Annotated[AsyncSession, Depends(get_db)]


async def init_db() -> None:
    """Initialise la base de données (pour tests ou premier démarrage)."""
    from app.db.base import Base
    
    logger.warning("⚠️  init_db() appelé - NE PAS utiliser en production!")
    
    async with engine.begin() as conn:
        # ATTENTION: DROP all tables puis recréer (destructif!)
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ Tables créées")


async def close_db() -> None:
    """Ferme proprement les connexions DB (shutdown)."""
    await engine.dispose()
    logger.info("🔌 Connexions DB fermées")