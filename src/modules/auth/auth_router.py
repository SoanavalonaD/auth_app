from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from src.modules.auth.auth_app import UserCreate, UserInDB, Token, UserLogin
from src.modules.auth.auth_app import AuthAppService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
router = APIRouter(
    prefix="/auth",
    tags=["Authentification"],
)


async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthAppService = Depends()
) -> int:
    """
    Dépendance qui valide le token JWT et retourne l'ID de l'utilisateur.
    """
    return await auth_service.get_current_user_id_from_token(token)


@router.post(
    "/register", 
    response_model=UserInDB, 
    status_code=status.HTTP_201_CREATED,
    summary="Enregistrer un nouvel utilisateur",
)
async def register(
    user_in: UserCreate, 
    auth_service: AuthAppService = Depends()
):
    """
    Point de terminaison pour l'inscription d'un nouvel utilisateur.
    Appelle le Service Applicatif pour gérer la logique d'inscription.
    """
    return await auth_service.register_new_user(user_in)

@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Authentification de l'utilisateur et obtention d'un jeton JWT",
)
async def login(
    user_login: UserLogin,
    auth_service: AuthAppService = Depends()
):
    """
    Point de terminaison pour la connexion.
    Valide les identifiants et retourne un jeton d'accès JWT.
    """
    return await auth_service.authenticate_user(user_login)


@router.get(
    "/users/me",
    summary="Récupère l'ID de l'utilisateur actuellement connecté",
)
async def read_users_me(
    # Le user_id est injecté par la dépendance 'get_current_user_id'
    current_user_id: int = Depends(get_current_user_id) 
):
    """
    Point de terminaison sécurisé. 
    Il retourne l'ID de l'utilisateur qui a fourni un jeton valide.
    Si le jeton est invalide ou manquant, FastAPI retourne 401 Unauthorized.
    """
    return {"user_id": current_user_id, "message": "Accès autorisé à la ressource protégée."}