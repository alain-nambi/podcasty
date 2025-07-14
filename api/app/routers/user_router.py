from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def welcome():
    """
    Retrieve a list of users.
    """
    return {"message": "Bienvenue sur l'API Podcast 🎧"}