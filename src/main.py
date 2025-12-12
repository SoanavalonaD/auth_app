from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.modules.auth.auth_router import router as auth_router


app = FastAPI(
    title="API d'Authentification Modulaire",
    description="Backend d'authentification utilisant FastAPI, SQLAlchemy et une architecture modulaire.",
    version="1.0.0",
)

# Configuration CORS pour permettre la communication avec le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default port
        "http://localhost:3000",  # Alternative React port
        "http://localhost:8080",  # Alternative dev port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion du router d'authentification avec préfixe /api/v1
app.include_router(auth_router, prefix="/api/v1")

@app.get("/", tags=["Root"], summary="Endpoint de base")
async def read_root():
    """
    Route de base pour vérifier que l'API est opérationnelle.
    """
    return {"message": "Bienvenue sur l'API d'Authentification. Rendez-vous sur /docs pour les endpoints."}

@app.get("/health", tags=["Health"], summary="Health check endpoint")
async def health_check():
    """
    Endpoint de santé pour vérifier que l'API est opérationnelle.
    Utilisé par les outils de monitoring et les orchestrateurs.
    """
    return {"status": "healthy", "service": "auth-api"}

# Ce bloc est utilisé par uvicorn si le fichier est exécuté directement, 
# mais Docker utilise la commande `fastapi run src/main.py`.
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)