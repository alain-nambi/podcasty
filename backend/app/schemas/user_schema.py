from tortoise.contrib.pydantic import pydantic_model_creator
from app.db.models import User

UserOut = pydantic_model_creator(
    User,
    name="UserOut",
    exclude=["hashed_password", "is_admin"]
)