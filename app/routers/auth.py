from fastapi import APIRouter, HTTPException, status
from tortoise.exceptions import IntegrityError
from app.db.models import User
from app.schemas.schemas import User_Pydantic, UserIn_Pydantic
from app.auth import verify_password, get_password_hash

router = APIRouter()

@router.post("/register/", response_model=User_Pydantic, status_code=status.HTTP_201_CREATED)
async def register(user: UserIn_Pydantic):
    """
    Crée un nouvel utilisateur s'il n'existe pas déjà dans la base de données.
    - Vérifie si l'email est déjà enregistré.
    - Hash le mot de passe.
    - Enregistre l'utilisateur en base.
    - Retourne les données (sans mot de passe) avec le modèle `User_Pydantic`.
    """

    # Vérifie si l'email existe déjà
    existing_user = await User.get_or_none(email=user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash du mot de passe avant l'enregistrement
    hashed_pw = get_password_hash(user.hashed_password)

    try:
        # Création de l'utilisateur
        user_obj = await User.create(
            username=user.username,
            email=user.email,
            hashed_password=hashed_pw
        )
    except IntegrityError:
        # En cas de conflit sur le username (ou autre contrainte unique)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Retour des données de l'utilisateur (sans le mot de passe)
    return await User_Pydantic.from_tortoise_orm(user_obj)
