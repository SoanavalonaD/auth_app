from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional
import re

# Schémas de base/DTO pour l'Entrée (Création/Mise à jour)
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = Field(default="", max_length=100)
    last_name: Optional[str] = Field(default="", max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Valide la complexité du mot de passe."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not re.search(r'[a-z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not re.search(r'[0-9]', v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schémas de Sortie (Réponse API)
class UserInDB(BaseModel):
    """Schéma Pydantic représentant les données de l'utilisateur dans la DB."""
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    """Schéma Pydantic pour la réponse JWT (Access Token)."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schéma Pydantic pour les données contenues dans le token (Payload)."""
    user_id: Optional[int] = None