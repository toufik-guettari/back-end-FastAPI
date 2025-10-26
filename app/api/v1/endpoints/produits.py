"""Endpoints REST pour l'entité Produit."""
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status
from sqlalchemy.exc import IntegrityError

from app.api.deps import DBSession, PaginationDep, SearchQuery
from app.core.logger import logger
from app.crud.produit import produit_crud
from app.exceptions import NotFoundError
from app.schemas.base import MessageResponse
from app.schemas.produit import ProduitCreate, ProduitList, ProduitRead, ProduitUpdate

router = APIRouter(prefix="/produits", tags=["Produits"])


@router.get(
    "/",
    response_model=ProduitList,
    summary="Lister les produits",
    description="Récupère la liste des produits avec pagination et recherche optionnelle",
)
async def list_produits(
    db: DBSession,
    pagination: PaginationDep,
    search: SearchQuery = None,
    en_stock: Annotated[bool | None, Query(description="Filtrer par disponibilité")] = None,
    min_prix: Annotated[float | None, Query(ge=0, description="Prix minimum")] = None,
    max_prix: Annotated[float | None, Query(ge=0, description="Prix maximum")] = None,
) -> ProduitList:
    """Liste les produits avec filtres optionnels."""
    
    logger.info(
        f"GET /produits - skip={pagination.skip}, limit={pagination.limit}, "
        f"search={search}, en_stock={en_stock}"
    )
    
    # Recherche par nom si query fournie
    if search:
        produits = await produit_crud.search_by_nom(
            db,
            query=search,
            limit=pagination.limit
        )
        total = len(produits)
    
    # Filtre par prix
    elif min_prix is not None or max_prix is not None:
        produits = await produit_crud.get_by_price_range(
            db,
            min_price=min_prix or 0,
            max_price=max_prix,
            skip=pagination.skip,
            limit=pagination.limit
        )
        total = await produit_crud.count(db)
    
    # Filtre par stock
    elif en_stock is not None:
        if en_stock:
            produits = await produit_crud.get_in_stock(
                db,
                skip=pagination.skip,
                limit=pagination.limit
            )
            total = await produit_crud.count_in_stock(db)
        else:
            # Produits hors stock (requête custom)
            all_produits = await produit_crud.get_multi(
                db,
                skip=pagination.skip,
                limit=pagination.limit
            )
            produits = [p for p in all_produits if not p.en_stock]
            total = await produit_crud.count(db)
    
    # Liste complète
    else:
        produits = await produit_crud.get_multi(
            db,
            skip=pagination.skip,
            limit=pagination.limit
        )
        total = await produit_crud.count(db)
    
    return ProduitList(produits=list(produits), total=total)


@router.post(
    "/",
    response_model=ProduitRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un produit",
    description="Crée un nouveau produit dans le catalogue",
)
async def create_produit(
    db: DBSession,
    produit_in: ProduitCreate,
) -> ProduitRead:
    """Crée un nouveau produit."""
    
    logger.info(f"POST /produits - nom={produit_in.nom}")
    
    # Vérifier si produit existe déjà
    existing = await produit_crud.get_by_nom(db, nom=produit_in.nom)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Un produit avec le nom '{produit_in.nom}' existe déjà (ID: {existing.id})"
        )
    
    try:
        produit = await produit_crud.create(db, obj_in=produit_in)
        logger.info(f"✅ Produit créé: ID={produit.id}")
        return produit
    
    except IntegrityError as e:
        logger.error(f"IntegrityError lors création produit: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Erreur d'intégrité des données"
        )


@router.get(
    "/{produit_id}",
    response_model=ProduitRead,
    summary="Récupérer un produit",
    description="Récupère un produit par son ID",
)
async def get_produit(
    db: DBSession,
    produit_id: Annotated[int, Path(ge=1, description="ID du produit")],
) -> ProduitRead:
    """Récupère un produit par ID."""
    
    logger.info(f"GET /produits/{produit_id}")
    
    produit = await produit_crud.get(db, id=produit_id)
    if not produit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produit avec ID {produit_id} non trouvé"
        )
    
    return produit


@router.put(
    "/{produit_id}",
    response_model=ProduitRead,
    summary="Mettre à jour un produit (complet)",
    description="Remplace entièrement un produit existant",
)
async def replace_produit(
    db: DBSession,
    produit_id: Annotated[int, Path(ge=1)],
    produit_in: ProduitCreate,  # PUT = remplacement complet
) -> ProduitRead:
    """Remplace un produit (mise à jour complète)."""
    
    logger.info(f"PUT /produits/{produit_id}")
    
    produit = await produit_crud.get(db, id=produit_id)
    if not produit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produit {produit_id} non trouvé"
        )
    
    # Convertir ProduitCreate en ProduitUpdate (tous les champs)
    update_data = ProduitUpdate(**produit_in.model_dump())
    updated = await produit_crud.update(db, db_obj=produit, obj_in=update_data)
    
    logger.info(f"✅ Produit {produit_id} remplacé")
    return updated


@router.patch(
    "/{produit_id}",
    response_model=ProduitRead,
    summary="Mettre à jour un produit (partiel)",
    description="Met à jour partiellement un produit (champs fournis uniquement)",
)
async def update_produit(
    db: DBSession,
    produit_id: Annotated[int, Path(ge=1)],
    produit_in: ProduitUpdate,
) -> ProduitRead:
    """Met à jour partiellement un produit."""
    
    logger.info(f"PATCH /produits/{produit_id} - {produit_in.model_dump(exclude_none=True)}")
    
    produit = await produit_crud.get(db, id=produit_id)
    if not produit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produit {produit_id} non trouvé"
        )
    
    updated = await produit_crud.update(db, db_obj=produit, obj_in=produit_in)
    logger.info(f"✅ Produit {produit_id} mis à jour")
    return updated


@router.delete(
    "/{produit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un produit",
    description="Supprime définitivement un produit du catalogue",
)
async def delete_produit(
    db: DBSession,
    produit_id: Annotated[int, Path(ge=1)],
) -> None:
    """Supprime un produit."""
    
    logger.info(f"DELETE /produits/{produit_id}")
    
    deleted = await produit_crud.delete(db, id=produit_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produit {produit_id} non trouvé"
        )
    
    logger.info(f"✅ Produit {produit_id} supprimé")


@router.get(
    "/stats/summary",
    response_model=dict,
    summary="Statistiques des produits",
    description="Retourne des statistiques globales sur le catalogue",
)
async def get_produits_stats(db: DBSession) -> dict:
    """Récupère les statistiques du catalogue."""
    
    logger.info("GET /produits/stats/summary")
    stats = await produit_crud.get_statistics(db)
    return stats