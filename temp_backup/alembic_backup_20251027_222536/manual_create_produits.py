"""create produits table

Revision ID: manual_create_produits
Revises: 9d358a87c15c
Create Date: 2025-01-27 22:20:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'manual_create_produits'
down_revision = '9d358a87c15c'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Créer la table produits
    op.create_table('produits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('prix', sa.Float(), nullable=False),
        sa.Column('en_stock', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id', name='pk_produits'),
        sa.CheckConstraint('length(nom) >= 2', name='ck_produits_nom_min_length'),
        sa.CheckConstraint('prix > 0', name='ck_produits_prix_positif')
    )
    
    # Créer les index
    op.create_index('ix_produits_id', 'produits', ['id'])
    op.create_index('ix_produits_nom', 'produits', ['nom'])

def downgrade() -> None:
    op.drop_table('produits')
