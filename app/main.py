from fastapi import FastAPI
from app.db.init import init_db
from app.routers import auth_router, user_router

app = FastAPI(
    title="Postcast API",
    version="1.0.0"
)

# Inclusion des routes définies dans les modules routers
app.include_router(user_router.router, prefix="/users", tags=["Users"])
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])

# Initialisation de la base de données
init_db(app)
