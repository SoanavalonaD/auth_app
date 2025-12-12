from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from src.modules.auth.auth_model import User
from src.modules.auth.auth_dto import UserCreate

class UserRepository:
    """
    Interface entre les services métier et la base de données.
    Contient la logique d'accès aux données (CRUD).
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def get_user_by_id(self, user_id: int) -> User | None:
        """Récupère un utilisateur par son ID."""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_user(self, user_in: UserCreate, hashed_password: str) -> User:
        """Crée un nouvel utilisateur avec gestion d'erreur pour les contraintes uniques."""
        try:
            db_user = User(
                email=user_in.email,
                hashed_password=hashed_password,
                first_name=user_in.first_name or "",
                last_name=user_in.last_name or "",
                is_active=True
            )
            self.db.add(db_user)
            await self.db.flush()  # Force l'ID à être rempli sans commit
            await self.db.refresh(db_user)  # Rafraîchit l'objet avec les données de la DB
            return db_user
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur avec cet email existe déjà"
            )