from fastapi import FastAPI
from app.db.init import init_db
from app.routers import user as user_router

app = FastAPI(title="Postcast API", version="1.0.0")
app.include_router(user_router.router)

init_db(app)