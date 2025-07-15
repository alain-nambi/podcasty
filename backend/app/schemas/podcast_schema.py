from tortoise.contrib.pydantic import pydantic_model_creator
from app.db.models import Podcast

PodcastOut = pydantic_model_creator(
    Podcast,
    name="PodcastOut",
)