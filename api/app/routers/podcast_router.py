# app/routers/podcast.py

from fastapi import APIRouter, UploadFile, File, Form, Depends, Request
from app.controllers.auth_controller import get_current_user_info
from app.controllers.podcast_controller import create_podcast
from app.schemas.podcast_schema import PodcastOut
from app.controllers.podcast_controller import stream_podcast_controller

router = APIRouter()


@router.post("/upload/", response_model=PodcastOut)
async def upload_podcast(
    current_user=Depends(get_current_user_info),
    title: str = Form(...),
    description: str = Form(...),
    duration: int = Form(...),
    audio_file: UploadFile = File(...),
    cover_image: UploadFile = File(None),
):
    return await create_podcast(
        title=title,
        description=description,
        duration=duration,
        audio_file=audio_file,
        cover_image=cover_image,
        author_id=current_user.id
    )


@router.get("/stream/{podcast_id}")
async def stream_podcast(podcast_id: int, request: Request, info: bool = False):
    return await stream_podcast_controller(podcast_id, request, info)


