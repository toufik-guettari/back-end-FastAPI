"""Configuration logging centralisé avec Loguru."""
import sys
import json
from pathlib import Path
from typing import Any

from loguru import logger

from app.core.config import settings


def serialize_record(record: dict[str, Any]) -> str:
    """Sérialise log en JSON pour production."""
    subset = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
    }
    
    # Ajouter extra fields si présents
    if record.get("extra"):
        subset["extra"] = record["extra"]
    
    # Ajouter exception si présente
    if record.get("exception"):
        subset["exception"] = record["exception"]
    
    return json.dumps(subset, ensure_ascii=False)


def configure_logging() -> None:
    """Configure Loguru selon l'environnement."""
    
    # Supprimer handler par défaut
    logger.remove()
    
    # Créer dossier logs si nécessaire
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_level = settings.LOG_LEVEL
    
    if settings.is_production:
        # Production : JSON structuré vers stdout (capturé par orchestrateur)
        logger.add(
            sys.stdout,
            level=log_level,
            format=serialize_record,
            serialize=True,
            backtrace=False,  # pas de traceback complet (perf)
            diagnose=False,   # pas de variables locales (sécurité)
        )
        
        # Fichier JSON avec rotation
        logger.add(
            log_dir / "app_{time:YYYY-MM-DD}.json",
            level=log_level,
            format=serialize_record,
            serialize=True,
            rotation="100 MB",  # rotation si fichier > 100MB
            retention="30 days",  # garder 30 jours
            compression="zip",  # compresser anciens logs
            backtrace=False,
            diagnose=False,
        )
    
    else:
        # Development : logs colorés lisibles
        logger.add(
            sys.stdout,
            level=log_level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            colorize=True,
            backtrace=True,   # traceback complet en dev
            diagnose=True,    # variables locales en dev
        )
        
        # Fichier texte avec rotation
        logger.add(
            log_dir / "app_{time:YYYY-MM-DD}.log",
            level="DEBUG",  # tout logger en fichier dev
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
                "{name}:{function}:{line} | {message}"
            ),
            rotation="50 MB",
            retention="7 days",  # moins de rétention en dev
            compression="zip",
        )
    
    # Log de démarrage
    logger.info(
        f"✅ Logging configuré - Env: {settings.APP_ENV}, Level: {log_level}"
    )


def get_logger():
    """Factory pour obtenir logger (utile pour dependency injection)."""
    return logger


# Configurer au import (exécuté une fois)
configure_logging()