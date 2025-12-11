import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.main import app
from src.config import settings
from src.data.domain import Base, get_db_session

# Import des modèles pour s'assurer qu'ils sont enregistrés dans Base.metadata
from src.modules.auth.auth_model import User

@pytest.fixture(scope="function")
async def db_session():
    """
    Fixture qui crée une session de base de données isolée pour chaque test.
    Elle crée les tables avant le test et les supprime après.
    """
    # Création d'un moteur spécifique pour le test (lié à la boucle d'événements du test)
    test_engine = create_async_engine(
        settings.DATABASE_URL,
        poolclass=NullPool, # Important pour éviter de garder des connexions ouvertes
        echo=False
    )
    
    # Création des tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Factory de session
    AsyncSessionLocal = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        yield session
        
    # Nettoyage : suppression des tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        
    await test_engine.dispose()

@pytest.fixture(scope="function")
async def async_client(db_session):
    """
    Fixture client qui surcharge la dépendance de base de données de l'application
    pour utiliser la session de test isolée.
    """
    async def override_get_db_session():
        yield db_session
        
    app.dependency_overrides[get_db_session] = override_get_db_session
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        yield client
        
    app.dependency_overrides.clear()
