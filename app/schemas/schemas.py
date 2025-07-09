from tortoise.contrib.pydantic import pydantic_model_creator
from app.db.models import User

User_Pydantic = pydantic_model_creator(User, name="User", exclude=["hashed_password"])
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True, exclude=["is_admin"])