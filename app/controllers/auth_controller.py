from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from tortoise.exceptions import IntegrityError, DoesNotExist
from jose import JWTError, jwt

from app.db.models import User
from app.schemas.schemas import User_Pydantic
from app.schemas.user import UserCreate
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    SECRET_KEY, ALGORITHM
)
from app.core.oauth2 import oauth2_scheme

# ✅ REGISTER A NEW USER
async def register_user(user: UserCreate):
    """
    Register a new user in the system.

    Input:
    {
        "username": "john",
        "email": "john@example.com",
        "hashed_password": "securepassword123"
    }

    Output (User_Pydantic):
    {
        "id": 1,
        "username": "john",
        "email": "john@example.com"
    }
    """
    existing_user = await User.get_or_none(email=user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_pw = get_password_hash(user.hashed_password)

    try:
        user_obj = await User.create(
            username=user.username,
            email=user.email,
            hashed_password=hashed_pw
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    return await User_Pydantic.from_tortoise_orm(user_obj)


# ✅ LOGIN A USER
async def login_user(form_data):
    """
    Authenticate a user and return a JWT token.

    Input (OAuth2PasswordRequestForm):
    {
        "username": "john@example.com",
        "password": "securepassword123"
    }

    Output:
    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
        "token_type": "bearer"
    }
    """
    try:
        user = await User.get(email=form_data.username)
    except DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# ✅ GET CURRENT LOGGED-IN USER FROM TOKEN
async def get_current_user_info(token: str = Depends(oauth2_scheme)):
    """
    Extract the current user info from the JWT token.

    Header:
        Authorization: Bearer <token>

    Output:
    {
        "id": 1,
        "username": "john",
        "email": "john@example.com"
    }
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = await User.get_or_none(email=email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return await User_Pydantic.from_tortoise_orm(user)
