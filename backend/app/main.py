from fastapi import FastAPI
from app.db.init import init_db
from app.routers import auth_router, user_router, podcast_router
from fastapi.middleware.cors import CORSMiddleware
import logging 

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

app = FastAPI(
    title="Postcast API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autoriser toutes les origines
    allow_credentials=True,
    allow_methods=["*"],  # Autoriser toutes les méthodes HTTP
    allow_headers=["*"],  # Autoriser tous les en-têtes
)

# Inclusion des routes définies dans les modules routers
app.include_router(user_router.router, prefix="/users", tags=["Users"])
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(podcast_router.router, prefix="/podcasts", tags=["Podcasts"])

# Initialisation de la base de données
init_db(app)
