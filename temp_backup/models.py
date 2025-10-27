from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Produit(Base):
    __tablename__ = "produits"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    prix = Column(Float, nullable=False)
    en_stock = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint('length(nom) >= 2', name='ck_produits_nom_min_length'),
        CheckConstraint('prix > 0', name='ck_produits_prix_positif'),
    )
