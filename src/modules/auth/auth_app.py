from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.data.domain import get_db_session
# Importation de UserLogin est essentielle pour authenticate_user
from src.modules.auth.auth_dto import UserCreate, UserInDB, Token, UserLogin 
from src.modules.auth.auth_repo import UserRepository
from src.modules.auth.auth_metier import get_password_hash, verify_password, create_access_token
from src.modules.auth.auth_model import User

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
        return UserInDB.model_validate(db_user)


    async def authenticate_user(self, user_login: UserLogin) -> Token:
        user: User | None = await self.repository.get_user_by_email(user_login.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
            
        if not verify_password(user_login.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
            
        if not user.is_active:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Compte inactif"
            )
        
        access_token = create_access_token(data={"sub": str(user.id)})
        return Token(access_token=access_token)