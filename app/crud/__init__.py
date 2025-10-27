"""CRUD package exports."""
from app.crud.base import CRUDBase
from app.crud.produit import CRUDProduit, produit_crud

__all__ = [
    "CRUDBase",
    "CRUDProduit",
    "produit_crud",
]