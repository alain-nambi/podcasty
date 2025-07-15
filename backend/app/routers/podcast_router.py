# app/routers/podcast.py

import logging
from fastapi import APIRouter, UploadFile, File, Form, Depends, Request
from app.controllers.auth_controller import get_current_user_info
from app.controllers.podcast_controller import create_podcast
from app.schemas.podcast_schema import PodcastOut
from app.controllers.podcast_controller import stream_podcast_controller, get_all_podcasts_by_user, get_podcast_by_id

router = APIRouter()

@router.get("/{podcast_id}")
async def get_podcast(podcast_id: int):
    """
    Retrieve a podcast by its ID.
    """
    return await get_podcast_by_id(podcast_id)

@router.get("/me")
async def get_my_podcasts(current_user=Depends(get_current_user_info)):
    """
    Retrieve podcasts for the current authenticated user.
    """
    return await get_all_podcasts_by_user(current_user.id)


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


