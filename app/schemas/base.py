"""Schémas Pydantic de base réutilisables."""
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class TimestampSchema(BaseModel):
    """Mixin pour timestamps dans les réponses."""
    
    created_at: datetime = Field(
        ...,
        description="Date de création (ISO 8601)",
        examples=["2024-01-15T10:30:00Z"]
    )
    updated_at: datetime = Field(
        ...,
        description="Date de dernière modification (ISO 8601)",
        examples=["2024-01-15T14:45:00Z"]
    )


class MessageResponse(BaseModel):
    """Schéma pour réponses simples avec message."""
    
    message: str = Field(..., description="Message de réponse")
    detail: str | None = Field(None, description="Détails supplémentaires")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "message": "Opération réussie",
                    "detail": "La ressource a été créée avec succès"
                }
            ]
        }
    )


class ErrorResponse(BaseModel):
    """Schéma pour réponses d'erreur standardisées."""
    
    error: str = Field(..., description="Type d'erreur")
    message: str = Field(..., description="Message d'erreur lisible")
    detail: str | None = Field(None, description="Détails techniques")
    path: str | None = Field(None, description="Chemin de la requête")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "error": "NotFound",
                    "message": "Ressource non trouvée",
                    "detail": "Produit avec ID 999 introuvable",
                    "path": "/produits/999"
                }
            ]
        }
    )


# Generic pour pagination
T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Schéma générique pour réponses paginées."""
    
    items: list[T] = Field(..., description="Liste des éléments")
    total: int = Field(..., ge=0, description="Nombre total d'éléments")
    page: int = Field(..., ge=1, description="Page courante")
    size: int = Field(..., ge=1, le=100, description="Taille de page")
    pages: int = Field(..., ge=0, description="Nombre total de pages")
    
    model_config = ConfigDict(from_attributes=True)