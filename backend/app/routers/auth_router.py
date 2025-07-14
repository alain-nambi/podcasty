from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.controllers.auth_controller import register_user, login_user, get_current_user_info
from app.schemas.schemas import User_Pydantic
from app.schemas.user import UserCreate

router = APIRouter()

@router.post("/register/", response_model=User_Pydantic)
async def register(user: UserCreate):
    return await register_user(user)

@router.post("/login/")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_user(form_data)

@router.get("/me/", response_model=User_Pydantic)
async def get_me(user_data=Depends(get_current_user_info)):
    return user_data