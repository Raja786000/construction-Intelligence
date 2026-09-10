import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "construction_risk.db"

MODEL_WEIGHTS = BASE_DIR / "risk_model" / "yolo11n.pt"
CONFIDENCE_THRESHOLD = 0.40
HIGH_RISK_SCORE_THRESHOLD = 70.0
MEDIUM_RISK_SCORE_THRESHOLD = 40.0

# Supported PPE Classes
CLASSES = {
    0: "hardhat",
    1: "no-hardhat",
    2: "vest",
    3: "no-vest",
    4: "mask",
    5: "no-mask",
    6: "harness",
    7: "person",
    8: "machinery",
    9: "fire",
    10: "smoke"
}
