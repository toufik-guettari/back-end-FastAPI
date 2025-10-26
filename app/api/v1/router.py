"""Router principal v1 agrégeant tous les endpoints."""
from fastapi import APIRouter

from app.api.v1.endpoints import produits

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(produits.router)