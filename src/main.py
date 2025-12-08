from fastapi import FastAPI
from src.modules.auth.auth_router import router as auth_router


app = FastAPI(
    title="API d'Authentification Modulaire",
    description="Backend d'authentification utilisant FastAPI, SQLAlchemy et une architecture modulaire.",
    version="1.0.0",
)
app.include_router(auth_router)

@app.get("/", tags=["Root"], summary="Endpoint de base")
async def read_root():
    """
    Route de base pour vérifier que l'API est opérationnelle.
    """
    return {"message": "Bienvenue sur l'API d'Authentification. Rendez-vous sur /docs pour les endpoints."}

# Ce bloc est utilisé par uvicorn si le fichier est exécuté directement, 
# mais Docker utilise la commande `fastapi run src/main.py`.
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)