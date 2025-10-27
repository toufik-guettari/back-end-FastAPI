"""Configuration Alembic ULTRA-SIMPLE et FONCTIONNELLE."""
from logging.config import fileConfig
from alembic import context
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
config = context.config
fileConfig(config.config_file_name)

# URL factice
config.set_main_option("sqlalchemy.url", "postgresql://user:pass@localhost/db")

try:
    from models import Base
    target_metadata = Base.metadata
    print("✅ Models importés")
except ImportError:
    target_metadata = None
    print("⚠️  Models non trouvés")

# CONFIGURATION MINIMALE - PAS de transaction pour les commandes standard
url = config.get_main_option("sqlalchemy.url")
context.configure(url=url, target_metadata=target_metadata)

# IMPORTANT: PAS de with context.begin_transaction() pour les commandes standard
context.run_migrations()
