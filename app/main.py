from fastapi import FastAPI
from app.db.init import init_db
from app.routers import user, auth

app = FastAPI(title="Postcast API", version="1.0.0")

# Inclusion des routes définies dans les modules routers
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

init_db(app)