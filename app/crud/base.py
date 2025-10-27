"""CRUD operations de base génériques."""
from typing import Generic, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Classe de base pour opérations CRUD génériques."""
    
    def __init__(self, model: Type[ModelType]):
        """
        Args:
            model: Modèle SQLAlchemy ORM
        """
        self.model = model
    
    async def get(
        self,
        session: AsyncSession,
        id: int
    ) -> ModelType | None:
        """Récupère un objet par ID."""
        result = await session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> list[ModelType]:
        """Récupère une liste d'objets avec pagination."""
        result = await session.execute(
            select(self.model)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count(self, session: AsyncSession) -> int:
        """Compte le nombre total d'objets."""
        from sqlalchemy import func
        result = await session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()
    
    async def create(
        self,
        session: AsyncSession,
        *,
        obj_in: CreateSchemaType
    ) -> ModelType:
        """Crée un nouvel objet."""
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Met à jour un objet existant."""
        obj_data = obj_in.model_dump(exclude_unset=True, exclude_none=True)
        
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj
    
    async def delete(
        self,
        session: AsyncSession,
        *,
        id: int
    ) -> ModelType | None:
        """Supprime un objet par ID."""
        obj = await self.get(session, id=id)
        if obj:
            await session.delete(obj)
            await session.commit()
        return obj