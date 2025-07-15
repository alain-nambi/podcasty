from tortoise.contrib.pydantic import pydantic_model_creator
from app.db.models import User
from pydantic import BaseModel
from typing import List, Optional

User_Pydantic = pydantic_model_creator(User, name="User", exclude=["hashed_password"])
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn_Pydantic", exclude_readonly=True, exclude=["is_admin"])



class CategoryOut(BaseModel):
    id: int
    name: str

class TagOut(BaseModel):
    id: int
    name: str

class PodcastIn(BaseModel):
    title: str
    category_ids: Optional[List[int]] = []
    tag_ids: Optional[List[int]] = []
