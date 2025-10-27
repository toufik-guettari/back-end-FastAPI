"""Dépendances réutilisables pour les routes."""
from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db


# Alias pour session DB
DBSession = Annotated[AsyncSession, Depends(get_db)]


# Pagination
class PaginationParams:
    """Paramètres de pagination réutilisables."""
    
    def __init__(
        self,
        skip: Annotated[int, Query(ge=0, description="Nombre d'éléments à sauter")] = 0,
        limit: Annotated[int, Query(ge=1, le=100, description="Nombre max d'éléments")] = 20,
    ):
        self.skip = skip
        self.limit = limit


PaginationDep = Annotated[PaginationParams, Depends()]


# Search query
SearchQuery = Annotated[
    str | None,
    Query(
        None,
        min_length=2,
        max_length=100,
        description="Requête de recherche",
        example="MacBook"
    )
]