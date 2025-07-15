# app/controllers/podcast_controller.py

import os, re, shutil, mimetypes, tempfile, logging
from typing import List, Dict, Any
import aiofiles
from fastapi import UploadFile, HTTPException
from app.db.models import Category, Podcast, Tag
from app.schemas.podcast_schema import PodcastOut
from fastapi import Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from tortoise.exceptions import DoesNotExist


from uuid import uuid4

from mutagen import File

MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)

async def get_podcast_by_id(podcast_id: int):
    """
    Retrieve a single podcast by its ID, including author details.
    """
    try:
        podcast = await Podcast.get_or_none(id=podcast_id).select_related("author")

        if not podcast:
            raise HTTPException(status_code=404, detail="Podcast not found")

        logging.info(f"[get_podcast_by_id] Fetched podcast ID: {podcast.id} by {getattr(podcast.author, 'username', 'unknown')}")

        return {
            "id": podcast.id,
            "title": podcast.title or "",
            "description": podcast.description or "",
            "audio_file": podcast.audio_file or "",
            "cover_image": podcast.cover_image,
            "duration": podcast.duration or 0,
            "created_at": podcast.created_at.isoformat() if podcast.created_at else None,
            # "updated_at": podcast.updated_at.isoformat() if podcast.updated_at else None,
            "author": {
                "id": getattr(podcast.author, "id", None),
                "username": getattr(podcast.author, "username", ""),
                "email": getattr(podcast.author, "email", "")
            }
        }

    except HTTPException:
        # Relever l’exception d'origine si elle est déjà lancée
        raise
    except Exception as e:
        logging.error(f"[get_podcast_by_id] Unexpected error for podcast ID {podcast_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_all_podcasts_by_user(user_id: int) -> List[Dict[str, Any]]:
    try:
        podcasts = await Podcast.filter(author_id=user_id).select_related("author")
    except DoesNotExist:
        logging.warning(f"No podcasts found for user {user_id}")
        return []

    results = []
    for p in podcasts:
        try:
            author_info = {
                "id": getattr(p.author, "id", None),
                "username": getattr(p.author, "username", ""),
                "email": getattr(p.author, "email", "")
            }

            podcast_data = {
                "id": p.id,
                "title": p.title or "",
                "description": p.description or "",
                "audio_file": p.audio_file or "",
                "cover_image": p.cover_image,
                "duration": p.duration or 0,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
                "author": author_info
            }

            results.append(podcast_data)

        except Exception as e:
            logging.error(f"[Podcast ID {getattr(p, 'id', 'unknown')}] Error: {e}")
            continue  # Skip faulty entries

    return results


async def create_podcast(
    title: str,
    description: str,
    duration: int,
    audio_file: UploadFile,
    cover_image: UploadFile | None,
    author_id: int,
    category_ids: list[int] | None = None,
    tag_ids: list[int] | None = None
) -> PodcastOut:
    audio_path = None
    cover_path = None
    temp_file_path = None

    try:
        if not audio_file.filename:
            raise HTTPException(status_code=400, detail="Nom de fichier audio manquant")

        os.makedirs(MEDIA_DIR, exist_ok=True)

        # Sauvegarde temporaire du fichier audio pour analyse
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1]) as temp_file:
            content = await audio_file.read()
            if len(content) == 0:
                raise HTTPException(status_code=400, detail="Le fichier audio est vide")
            temp_file.write(content)
            temp_file_path = temp_file.name

        await audio_file.seek(0)

        # Analyse de la durée avec Mutagen
        audio = File(temp_file_path)
        if audio is None or audio.info is None:
            raise HTTPException(status_code=400, detail="Format audio non supporté")

        audio_duration = int(audio.info.length)
        if audio_duration <= 0:
            raise HTTPException(status_code=400, detail="Durée audio non valide")

        # Suppression du fichier temporaire
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            temp_file_path = None

        # Sauvegarde définitive du fichier audio
        audio_filename = f"{uuid4().hex}_{audio_file.filename}"
        audio_path = os.path.join(MEDIA_DIR, audio_filename)
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        # Traitement de l'image de couverture
        if cover_image and cover_image.filename:
            cover_filename = f"{uuid4().hex}_{cover_image.filename}"
            cover_path = os.path.join(MEDIA_DIR, cover_filename)
            with open(cover_path, "wb") as buffer:
                shutil.copyfileobj(cover_image.file, buffer)

        # Création du podcast en base
        podcast = await Podcast.create(
            title=title,
            description=description,
            audio_file=audio_path,
            cover_image=cover_path,
            duration=audio_duration,
            author_id=author_id,
        )

        # Ajout des catégories si fournies
        if category_ids:
            categories = await Category.filter(id__in=category_ids)
            await podcast.categories.add(*categories)

        # Ajout des tags si fournis
        if tag_ids:
            tags = await Tag.filter(id__in=tag_ids)
            await podcast.tags.add(*tags)

        return await PodcastOut.from_tortoise_orm(podcast)

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Erreur lors de la création du podcast: {str(e)}")
        # Nettoyage fichiers en cas d'erreur
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
        if cover_path and os.path.exists(cover_path):
            os.remove(cover_path)
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")


# Taille des morceaux envoyés au client pendant le streaming (64 Ko)
CHUNK_SIZE = 1024 * 64  # 64 Ko


# 🎯 Fonction utilitaire pour récupérer le chemin du fichier
async def get_podcast_stream(podcast_id: int) -> str:
    podcast = await Podcast.get_or_none(id=podcast_id)
    if not podcast or not podcast.audio_file:
        raise HTTPException(status_code=404, detail="Podcast not found")
    return podcast


# 🎧 Contrôleur principal pour le stream audio avec ou sans Range
async def stream_podcast_controller(podcast_id: int, request: Request, info: bool = False):
    """
    Stream un fichier audio avec support de "Range", ou retourne les infos en JSON avec ?info=true.
    
    Args:
        podcast_id (int): identifiant du podcast à streamer.
        request (Request): objet FastAPI contenant les headers (ex: 'Range').
        info (bool): si vrai, retourne les métadonnées du fichier audio.

    Returns:
        StreamingResponse ou JSONResponse : soit le flux audio, soit les informations du fichier.
    """

    # 🧭 1. Récupération du chemin du fichier selon l'ID
    podcast = await get_podcast_stream(podcast_id)
    audio_path = podcast.audio_file

    # 🛑 2. Vérification de l'existence physique du fichier
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Fichier audio introuvable")

    # 📏 3. Récupération de la taille et du type MIME du fichier
    file_size = os.path.getsize(audio_path)
    mime_type, _ = mimetypes.guess_type(audio_path)
    mime_type = mime_type or "application/octet-stream"

    # 🧾 4. Mode d'information : retourne les métadonnées du podcast
    if info:
        stream_url = str(request.base_url) + f"podcasts/stream/{podcast_id}"
        return JSONResponse({
            "podcast_id": podcast_id,
            "file_name": os.path.basename(audio_path),
            "file_size": file_size,
            "mime_type": mime_type,
            "stream_url": stream_url,
            "status": "ready",
            "duration": podcast.duration,  # Placeholder, peut être remplacé par la durée réelle
        })

    # 🔍 5. Gestion du header "Range" (lecture partielle demandée par le client)
    range_header = request.headers.get("range")
    if range_header:
        # 📚 5.1 Extraction des bornes de la plage demandée
        match = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else file_size - 1
            end = min(end, file_size - 1)
            length = end - start + 1

            # 🔁 5.2 Lecture du fichier depuis la position "start" jusqu'à "end"
            async def iter_range():
                async with aiofiles.open(audio_path, "rb") as f:
                    await f.seek(start)
                    bytes_remaining = length
                    while bytes_remaining > 0:
                        chunk_size = min(CHUNK_SIZE, bytes_remaining)
                        data = await f.read(chunk_size)
                        if not data:
                            break
                        bytes_remaining -= len(data)
                        yield data

            # 📦 5.3 Création de la réponse partielle (206 Partial Content)
            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(length),
            }

            return StreamingResponse(
                iter_range(),
                status_code=206,
                media_type=mime_type,
                headers=headers,
            )

    # 🎬 6. Si aucun "Range", lecture complète du fichier
    async def iter_full():
        async with aiofiles.open(audio_path, "rb") as f:
            while True:
                chunk = await f.read(CHUNK_SIZE)
                if not chunk:
                    break
                yield chunk

    # 📦 7. Création de la réponse complète (200 OK)
    headers = {
        "Content-Length": str(file_size),
        "Accept-Ranges": "bytes",  # informe que le serveur supporte le Range
    }

    return StreamingResponse(
        iter_full(),
        media_type=mime_type,
        headers=headers,
    )
