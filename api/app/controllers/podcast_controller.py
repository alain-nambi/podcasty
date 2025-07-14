# app/controllers/podcast_controller.py

import os, re, shutil, mimetypes
import aiofiles
from fastapi import UploadFile, HTTPException
from app.db.models import Podcast
from app.schemas.podcast_schema import PodcastOut
from fastapi import Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse


from uuid import uuid4

MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)


async def create_podcast(
    title: str,
    description: str,
    duration: int,
    audio_file: UploadFile,
    cover_image: UploadFile | None,
    author_id: int
) -> PodcastOut:
    # ✅ Créer le dossier de stockage s'il n'existe pas
    os.makedirs(MEDIA_DIR, exist_ok=True)

    # ✅ Générer un nom unique pour le fichier audio pour éviter les conflits
    audio_filename = f"{uuid4().hex}_{audio_file.filename}"
    audio_path = os.path.join(MEDIA_DIR, audio_filename)

    # ✅ Sauvegarder physiquement le fichier audio sur le disque
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)

    # ✅ Préparer la variable pour le chemin de l’image de couverture
    cover_path = None
    if cover_image:
        # ✅ Générer un nom unique pour l’image de couverture
        cover_filename = f"{uuid4().hex}_{cover_image.filename}"
        cover_path = os.path.join(MEDIA_DIR, cover_filename)

        # ✅ Sauvegarder physiquement l’image de couverture sur le disque
        with open(cover_path, "wb") as buffer:
            shutil.copyfileobj(cover_image.file, buffer)

    # ✅ Créer un enregistrement du podcast dans la base de données
    podcast = await Podcast.create(
        title=title,
        description=description,
        audio_file=audio_path,   # chemin du fichier audio sur le disque
        cover_image=cover_path,  # chemin de l'image si elle existe
        duration=duration,
        author_id=author_id
    )

    # ✅ Retourner une version "schéma" du podcast, pour réponse client
    return await PodcastOut.from_tortoise_orm(podcast)

# Taille des morceaux envoyés au client pendant le streaming (64 Ko)
CHUNK_SIZE = 1024 * 64  # 64 Ko

# 🎯 Fonction utilitaire pour récupérer le chemin du fichier
async def get_podcast_stream(podcast_id: int) -> str:
    podcast = await Podcast.get_or_none(id=podcast_id)
    if not podcast or not podcast.audio_file:
        raise HTTPException(status_code=404, detail="Podcast not found")
    return podcast.audio_file


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
    audio_path = await get_podcast_stream(podcast_id)

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
            "status": "ready"
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
