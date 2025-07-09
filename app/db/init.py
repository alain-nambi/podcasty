# Connexion to the database and initialization of Tortoise ORM
from tortoise.contrib.fastapi import register_tortoise
from app.core.config import DB_URL

def init_db(app):
    register_tortoise(
        app=app,
        db_url=DB_URL,
        modules={"models": ["app.db.models"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )