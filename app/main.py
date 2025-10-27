"""Application FastAPI principale avec middlewares et lifecycle."""
import sentry_sdk
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import api_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logger import logger
from app.db.session import close_db, engine
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.timing import TimingMiddleware

from sqlalchemy import text
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie (startup/shutdown)."""
    # Startup
    logger.info(f"🚀 Démarrage {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📍 Environnement: {settings.APP_ENV}")
    logger.info(f"🔌 Base de données: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")

    # Test connexion DB
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Connexion DB OK")
    except Exception as e:
        logger.error(f"❌ Erreur connexion DB: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Arrêt de l'application...")
    await close_db()
    logger.info("✅ Connexions DB fermées")


# ===== INITIALISATION SENTRY =====
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.APP_ENV,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=0.1 if settings.is_production else 0.0,
        enable_tracing=True,
    )
    logger.info("✅ Sentry initialisé")


# ===== APPLICATION FASTAPI =====
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de gestion de produits avec FastAPI, SQLAlchemy async, et Pydantic v2",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    debug=settings.DEBUG,
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "docExpansion": "list",
        "filter": True,
    },
)


# ===== MIDDLEWARES =====
if settings.is_production:
    # Trusted Host (protection contre host header attacks)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "*.yourdomain.com"],
    )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)

# Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom middlewares
app.add_middleware(TimingMiddleware)
app.add_middleware(RequestIDMiddleware)


# ===== EXCEPTION HANDLERS =====
register_exception_handlers(app)


# ===== ROUTES =====
app.include_router(api_router)


@app.get("/", tags=["Root"])
async def root():
    """Endpoint racine avec informations de l'API."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "docs": "/docs" if not settings.is_production else "disabled",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Healthcheck simple (liveness probe)."""
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness check avec test connexion DB."""
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not_ready",
            "database": "disconnected",
            "error": str(e),
        }


# ===== OBSERVABILITÉ =====
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


# ===== ENTRY POINT =====
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.is_development,
        workers=1 if settings.is_development else settings.WORKERS,
        log_level="info",
    )
