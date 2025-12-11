import pytest
from httpx import AsyncClient

# Marqueur pour indiquer que tous les tests de ce fichier sont asynchrones
pytestmark = pytest.mark.asyncio

async def test_root(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API d'Authentification. Rendez-vous sur /docs pour les endpoints."}

async def test_register_user(async_client: AsyncClient):
    payload = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = await async_client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data
    assert "is_active" in data

async def test_login_user(async_client: AsyncClient):
    # D'abord on enregistre (au cas où l'ordre des tests n'est pas garanti ou DB vide)
    # Idéalement on utiliserait une fixture pour créer un user
    payload = {
        "email": "login_test@example.com",
        "password": "password123"
    }
    await async_client.post("/auth/register", json=payload)

    login_payload = {
        "email": "login_test@example.com",
        "password": "password123"
    }
    response = await async_client.post("/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
