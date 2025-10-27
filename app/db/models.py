"""Modèles ORM SQLAlchemy."""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TimestampMixin:
    """Mixin pour ajouter created_at/updated_at automatiquement."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Date de création"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Date de dernière modification"
    )


class Produit(Base, TimestampMixin):
    """Modèle Produit avec contraintes et index."""
    
    __tablename__ = "produits"
    
    # Colonnes avec type hints (Mapped pour mypy)
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        comment="Identifiant unique"
    )
    
    nom: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        comment="Nom du produit"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Description détaillée"
    )
    
    prix: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Prix unitaire en euros"
    )
    
    en_stock: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        server_default="true",
        comment="Disponibilité en stock"
    )
    
    # Contraintes au niveau DB (validation côté SQL)
    __table_args__ = (
        CheckConstraint("prix > 0", name="prix_positif"),
        CheckConstraint("length(nom) >= 2", name="nom_min_length"),
        {"comment": "Table des produits du catalogue"}
    )
    
    def __repr__(self) -> str:
        return (
            f"Produit(id={self.id}, nom={self.nom!r}, "
            f"prix={self.prix:.2f}€, en_stock={self.en_stock})"
        )