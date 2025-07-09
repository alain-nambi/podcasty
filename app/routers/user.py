from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def welcome():
    """
    Retrieve a list of users.
    """
    return {"message": "Bienvenue sur l'API Podcast 🎧"}