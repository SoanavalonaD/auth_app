from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
import logging

from src.data.domain import get_db_session
from src.modules.auth.auth_dto import UserCreate, UserInDB, Token, UserLogin, TokenData
from src.modules.auth.auth_repo import UserRepository
from src.modules.auth.auth_metier import get_password_hash, verify_password, create_access_token
from src.modules.auth.auth_model import User
from src.config import settings

logger = logging.getLogger(__name__)


class AuthAppService:
    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        self.repository = UserRepository(db)


    async def register_new_user(self, user_in: UserCreate) -> UserInDB:
        """Logique d'inscription: vérifie l'existence, hache le mot de passe et crée l'utilisateur."""
        existing_user = await self.repository.get_user_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur avec cet email existe déjà"
            )

        hashed_password = get_password_hash(user_in.password)
        db_user = await self.repository.create_user(user_in, hashed_password)
        logger.info(f"Nouvel utilisateur créé: {db_user.email}")
        return UserInDB.model_validate(db_user)


    async def authenticate_user(self, user_login: UserLogin) -> Token:
        user: User | None = await self.repository.get_user_by_email(user_login.email)
        
        if not user:
            logger.warning(f"Tentative de connexion échouée pour: {user_login.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
            
        if not verify_password(user_login.password, user.hashed_password):
            logger.warning(f"Mot de passe incorrect pour: {user_login.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
            
        if not user.is_active:
            logger.warning(f"Tentative de connexion avec compte inactif: {user_login.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Compte inactif"
            )
        
        access_token = create_access_token(data={"sub": str(user.id)})
        logger.info(f"Connexion réussie pour: {user_login.email}")
        return Token(access_token=access_token)
    
    async def get_current_user_id_from_token(self, token: str) -> int:
        """
        Valide le token JWT et vérifie que l'utilisateur existe toujours en base.
        """
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )

            user_id_str: str = payload.get("sub")
            if user_id_str is None:
                raise JWTError("Sub field missing in token payload")

            user_id = int(user_id_str)
            
            # Vérifier que l'utilisateur existe toujours et est actif
            user = await self.repository.get_user_by_id(user_id)
            if not user or not user.is_active:
                logger.warning(f"Token valide mais utilisateur inexistant ou inactif: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Utilisateur invalide ou inactif",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            token_data = TokenData(user_id=user_id)

        except JWTError as e:
            logger.warning(f"JWT validation failed: {type(e).__name__}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide ou expiré.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return token_data.user_id
    