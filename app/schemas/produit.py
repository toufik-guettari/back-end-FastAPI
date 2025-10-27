"""Schémas Pydantic pour l'entité Produit."""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.base import TimestampSchema


class ProduitBase(BaseModel):
    """Schéma de base partagé entre Create et Update."""
    
    nom: Annotated[str, Field(
        min_length=2,
        max_length=200,
        description="Nom du produit",
        examples=["MacBook Pro 16\"", "iPhone 15 Pro"]
    )]
    
    description: Annotated[str | None, Field(
        None,
        max_length=5000,
        description="Description détaillée du produit",
        examples=["Ordinateur portable haute performance avec puce M3 Max"]
    )]
    
    prix: Annotated[float, Field(
        gt=0,
        le=1_000_000,
        description="Prix unitaire en euros (strictement positif)",
        examples=[1299.99, 49.90]
    )]
    
    en_stock: Annotated[bool, Field(
        default=True,
        description="Disponibilité en stock",
        examples=[True, False]
    )]
    
    @field_validator("nom")
    @classmethod
    def validate_nom(cls, v: str) -> str:
        """Valide et normalise le nom."""
        # Supprimer espaces multiples
        v = " ".join(v.split())
        
        # Vérifier caractères interdits
        forbidden_chars = ["<", ">", "{", "}", "|", "\\"]
        if any(char in v for char in forbidden_chars):
            raise ValueError(f"Le nom contient des caractères interdits: {forbidden_chars}")
        
        return v.strip()
    
    @field_validator("prix")
    @classmethod
    def validate_prix(cls, v: float) -> float:
        """Arrondit le prix à 2 décimales."""
        return round(v, 2)


class ProduitCreate(ProduitBase):
    """Schéma pour création d'un produit (POST)."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "nom": "Casque Sony WH-1000XM5",
                    "description": "Casque antibruit sans fil de haute qualité",
                    "prix": 379.99,
                    "en_stock": True
                }
            ]
        }
    )


class ProduitUpdate(BaseModel):
    """Schéma pour mise à jour partielle d'un produit (PATCH/PUT)."""
    
    nom: Annotated[str | None, Field(
        None,
        min_length=2,
        max_length=200,
        description="Nouveau nom du produit"
    )]
    
    description: Annotated[str | None, Field(
        None,
        max_length=5000,
        description="Nouvelle description"
    )]
    
    prix: Annotated[float | None, Field(
        None,
        gt=0,
        le=1_000_000,
        description="Nouveau prix"
    )]
    
    en_stock: Annotated[bool | None, Field(
        None,
        description="Nouvelle disponibilité"
    )]
    
    @field_validator("nom")
    @classmethod
    def validate_nom(cls, v: str | None) -> str | None:
        """Valide le nom si fourni."""
        if v is None:
            return v
        v = " ".join(v.split())
        forbidden_chars = ["<", ">", "{", "}", "|", "\\"]
        if any(char in v for char in forbidden_chars):
            raise ValueError(f"Le nom contient des caractères interdits: {forbidden_chars}")
        return v.strip()
    
    @field_validator("prix")
    @classmethod
    def validate_prix(cls, v: float | None) -> float | None:
        """Arrondit le prix si fourni."""
        return round(v, 2) if v is not None else None
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "prix": 349.99,
                    "en_stock": False
                }
            ]
        }
    )


class ProduitRead(ProduitBase, TimestampSchema):
    """Schéma pour lecture d'un produit (GET response)."""
    
    id: Annotated[int, Field(
        ...,
        ge=1,
        description="Identifiant unique du produit",
        examples=[1, 42]
    )]
    
    model_config = ConfigDict(
        from_attributes=True,  # Permet lecture depuis ORM (ex orm_mode v1)
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "nom": "MacBook Pro 16\"",
                    "description": "Ordinateur portable haute performance",
                    "prix": 2799.00,
                    "en_stock": True,
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z"
                }
            ]
        }
    )


class ProduitList(BaseModel):
    """Schéma pour liste de produits (GET /produits)."""
    
    produits: list[ProduitRead] = Field(
        ...,
        description="Liste des produits"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Nombre total de produits"
    )
    
    model_config = ConfigDict(from_attributes=True)