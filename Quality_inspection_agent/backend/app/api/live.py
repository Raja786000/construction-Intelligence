from pathlib import Path
import cv2
from fastapi import APIRouter, File, UploadFile

from .live_engine import LiveQualityEngine

router = APIRouter(tags=["Live Quality Monitor"])
engine = LiveQualityEngine()


@router.get("/status")
def live_status():
    return engine.status()


@router.post("/frame")
async def live_frame(frame: UploadFile = File(...)):
    data = await frame.read()
    image = cv2.imdecode(__import__("numpy").frombuffer(data, dtype=__import__("numpy").uint8), cv2.IMREAD_COLOR)
    if image is None:
        return {"enabled": True, "mode": "Enhanced live CV", "width": 1280, "height": 720, "detections": [], "validated": True, "error": "Invalid camera frame."}

    height, width = image.shape[:2]
    detections, mode, _ = engine.analyze(image)
    return {
        "enabled": True,
        "mode": mode,
        "width": width,
        "height": height,
        "detections": detections,
        "validated": True,
        "human_regions_suppressed": True,
    }
