"""CRUD operations spécifiques pour Produit."""
from typing import Sequence

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.db.models import Produit
from app.schemas.produit import ProduitCreate, ProduitUpdate


class CRUDProduit(CRUDBase[Produit, ProduitCreate, ProduitUpdate]):
    """CRUD operations pour l'entité Produit."""
    
    async def get_by_nom(
        self,
        session: AsyncSession,
        *,
        nom: str
    ) -> Produit | None:
        """Récupère un produit par son nom exact."""
        result = await session.execute(
            select(Produit).where(Produit.nom == nom)
        )
        return result.scalar_one_or_none()
    
    async def search_by_nom(
        self,
        session: AsyncSession,
        *,
        query: str,
        limit: int = 50
    ) -> Sequence[Produit]:
        """Recherche produits par nom (LIKE insensible à la casse)."""
        search_pattern = f"%{query}%"
        result = await session.execute(
            select(Produit)
            .where(Produit.nom.ilike(search_pattern))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_in_stock(
        self,
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Produit]:
        """Récupère uniquement les produits en stock."""
        result = await session.execute(
            select(Produit)
            .where(Produit.en_stock == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_price_range(
        self,
        session: AsyncSession,
        *,
        min_price: float = 0,
        max_price: float | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Produit]:
        """Récupère produits dans une fourchette de prix."""
        query = select(Produit).where(Produit.prix >= min_price)
        
        if max_price is not None:
            query = query.where(Produit.prix <= max_price)
        
        query = query.offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()
    
    async def bulk_update_stock(
        self,
        session: AsyncSession,
        *,
        product_ids: list[int],
        en_stock: bool
    ) -> int:
        """Met à jour le stock pour plusieurs produits."""
        from sqlalchemy import update
        
        stmt = (
            update(Produit)
            .where(Produit.id.in_(product_ids))
            .values(en_stock=en_stock)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount  # type: ignore
    
    async def count_in_stock(self, session: AsyncSession) -> int:
        """Compte le nombre de produits en stock."""
        from sqlalchemy import func
        result = await session.execute(
            select(func.count())
            .select_from(Produit)
            .where(Produit.en_stock == True)
        )
        return result.scalar_one()
    
    async def get_statistics(self, session: AsyncSession) -> dict:
        """Calcule statistiques sur les produits."""
        from sqlalchemy import func
        
        result = await session.execute(
            select(
                func.count(Produit.id).label("total"),
                func.count(Produit.id).filter(Produit.en_stock == True).label("in_stock"),
                func.avg(Produit.prix).label("avg_price"),
                func.min(Produit.prix).label("min_price"),
                func.max(Produit.prix).label("max_price"),
            )
        )
        row = result.one()
        
        return {
            "total": row.total,
            "in_stock": row.in_stock,
            "out_of_stock": row.total - row.in_stock,
            "avg_price": round(float(row.avg_price or 0), 2),
            "min_price": float(row.min_price or 0),
            "max_price": float(row.max_price or 0),
        }


# Instance singleton pour utilisation dans les routes
produit_crud = CRUDProduit(Produit)