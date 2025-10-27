"""Schemas package exports."""
from app.schemas.base import ErrorResponse, MessageResponse, PaginatedResponse, TimestampSchema
from app.schemas.produit import (
    ProduitBase,
    ProduitCreate,
    ProduitList,
    ProduitRead,
    ProduitUpdate,
)

__all__ = [
    # Base
    "TimestampSchema",
    "MessageResponse",
    "ErrorResponse",
    "PaginatedResponse",
    # Produit
    "ProduitBase",
    "ProduitCreate",
    "ProduitUpdate",
    "ProduitRead",
    "ProduitList",
]