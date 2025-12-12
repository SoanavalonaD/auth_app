from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from src.config import settings
import logging

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe simple correspond au mot de passe haché."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hache le mot de passe simple."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Crée un token JWT avec une durée d'expiration.
    Par défaut: 24 heures.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Token valide pour 24 heures par défaut
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    
    # Ajout du temps d'émission pour plus de sécurité (iat: issued at)
    to_encode.update({"iat": datetime.now(timezone.utc)}) 
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    logger.info(f"Token créé avec expiration: {expire}")
    return encoded_jwt