from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    Configuration de l'application chargée depuis les variables d'environnement.
    Utilise Pydantic pour la validation et la gestion des types.
    """
    
    # Configuration de l'API
    SECRET_KEY: str = Field(..., description="Clé secrète pour le hachage des tokens JWT")
    ALGORITHM: str = Field("HS256", description="Algorithme de signature JWT")
    API_PORT: int = Field(8000, description="Port de l'API")

    # Configuration de la Base de Données
    DATABASE_URL: str = Field(..., description="URL de connexion complète à la base de données (postgresql+asyncpg)")
    
    # Configuration du modèle Pydantic
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore' # Ignorer les variables d'environnement non définies ici
    )

# Instance de la configuration
settings = Settings()

# Affichage de l'URL sans le mot de passe pour le débogage (sécurité)
def get_db_url_safe():
    """Retourne l'URL de la base de données en masquant le mot de passe."""
    url = settings.DATABASE_URL
    if "@" in url:
        try:
            # Tente de masquer le mot de passe dans l'URL
            parts = url.split("://")[1].split("@")
            user_pass = parts[0].split(":")
            host_port = parts[1]
            return f"{url.split('://')[0]}://{user_pass[0]}:***@{host_port}"
        except IndexError:
            return url # Retourne l'URL brute si le format n'est pas celui attendu
    return url

print(f"Configuration chargée. DB URL: {get_db_url_safe()}")