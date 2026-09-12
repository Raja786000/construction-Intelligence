from pathlib import Path
import shutil
import uuid
from fastapi import UploadFile

BASE = Path(__file__).resolve().parents[2]
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)
ALLOWED = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

async def save_upload(upload: UploadFile):
    ext = Path(upload.filename or "").suffix.lower()
    if ext not in ALLOWED:
        raise ValueError("Unsupported image type")
    name = f"{uuid.uuid4()}{ext}"
    path = UPLOADS / name
    with path.open("wb") as out:
        shutil.copyfileobj(upload.file, out)
    return path, name
