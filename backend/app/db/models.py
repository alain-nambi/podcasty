from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    hashed_password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    is_admin = fields.BooleanField(default=False)
    
    class Meta:
        table = "users"
        
class Podcast(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField()
    audio_file = fields.CharField(max_length=255)
    cover_image = fields.CharField(max_length=255, null=True)
    author = fields.ForeignKeyField("models.User", related_name="podcasts")
    duration = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    categories = fields.ManyToManyField("models.Category", related_name="podcasts", through="podcast_category")
    tags = fields.ManyToManyField("models.Tag", related_name="podcasts", through="podcast_tag")
    
    class Meta:
        table = "podcasts"
        
class Category(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    podcasts: fields.ManyToManyRelation["Podcast"]
    
    class Meta:
        table = "categories"  # pluriel recommandé

class Tag(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    podcasts: fields.ManyToManyRelation["Podcast"]
    
    class Meta:
        table = "tags"  # pluriel recommandé
