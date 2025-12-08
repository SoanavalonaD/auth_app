from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import settings

Base = declarative_base()

# 1. Création du moteur Asynchrone
# Utilise l'URL de la base de données définie dans config.py
async_engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=False, # Mettre à True pour le débogage SQL
    future=True
)

# 2. Création de la Session Locale Asynchrone
AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dépendance FastAPI pour injecter une session DB asynchrone.
    Ouvre une session au début de la requête et la ferme (ou la rollback) à la fin.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# 3. Fonction pour Alembic
def get_base_metadata():
    """
    Retourne les métadonnées de la Base pour la configuration d'Alembic.
    Ceci est utilisé dans src/alembic/env.py.
    """
    return Base.metadata