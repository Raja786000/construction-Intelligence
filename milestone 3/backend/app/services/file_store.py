from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile
import shutil

BASE = Path(__file__).resolve().parents[2]
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)

ALLOWED = {
    ".pdf", ".docx", ".txt", ".md", ".csv", ".xlsx",
    ".png", ".jpg", ".jpeg", ".webp"
}

async def save_uploads(files):
    saved = []
    for f in files:
        if not f.filename:
            continue
        ext = Path(f.filename).suffix.lower()
        if ext not in ALLOWED:
            raise ValueError(f"Unsupported file type: {ext}")
        safe = Path(f.filename).name.replace(" ", "_")
        name = f"{uuid4().hex}_{safe}"
        target = UPLOADS / name
        with target.open("wb") as out:
            shutil.copyfileobj(f.file, out)
        saved.append({
            "document_id": uuid4().hex,
            "filename": f.filename,
            "stored_name": name,
            "path": str(target),
            "url": f"/uploads/{name}",
            "extension": ext,
            "size_bytes": target.stat().st_size
        })
    return saved
