"""Base déclarative SQLAlchemy avec conventions de naming."""
from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr


# Convention de naming pour contraintes (facilite migrations)
convention = {
    "ix": "ix_%(column_0_label)s",  # Index
    "uq": "uq_%(table_name)s_%(column_0_name)s",  # Unique
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # Check
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # Foreign Key
    "pk": "pk_%(table_name)s",  # Primary Key
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    """Classe de base pour tous les modèles ORM."""
    
    metadata = metadata
    
    # Attributs automatiques pour tous les modèles
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Génère nom de table automatiquement (snake_case du nom classe)."""
        # Convertir CamelCase en snake_case
        import re
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        return name
    
    def __repr__(self) -> str:
        """Représentation générique des modèles."""
        attrs = ", ".join(
            f"{k}={v!r}" 
            for k, v in self.__dict__.items() 
            if not k.startswith("_")
        )
        return f"{self.__class__.__name__}({attrs})"