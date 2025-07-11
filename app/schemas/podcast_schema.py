# Import de la fonction utilitaire pour créer automatiquement un modèle Pydantic
# à partir d'un modèle Tortoise ORM
from tortoise.contrib.pydantic import pydantic_model_creator
from app.db.models import Podcast

# Création automatique du schéma Pydantic PodcastOut à partir du modèle Podcast.
# Ce schéma sera utilisé pour sérialiser les réponses (ex : lors de la création d’un podcast).
# Il inclura tous les champs du modèle Podcast (id, title, description, etc.)
PodcastOut = pydantic_model_creator(
    Podcast,
    name="PodcastOut",
    exclude=("audio_file", "cover_image", "created_at", "updated_at")
)
