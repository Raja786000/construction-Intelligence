from pathlib import Path
import os

BASE = Path(__file__).resolve().parents[2]
MODEL_DIR = Path(os.getenv("QUALITY_MODEL_DIR", BASE.parent / "models"))

MODEL_CONFIG = {
    "crack": MODEL_DIR / "crack" / "model.pt",
    "concrete": MODEL_DIR / "concrete" / "model.pt",
    "surface": MODEL_DIR / "surface" / "model.pt",
    "component": MODEL_DIR / "component" / "model.pt",
    "corrosion": MODEL_DIR / "corrosion" / "model.pt",
}
LIVE_YOLO = os.getenv("YOLO_LIVE_MODEL_PATH", "")
