from pathlib import Path
import os
ROOT=Path(__file__).resolve().parent
MODEL_WEIGHTS=os.getenv('RISK_MODEL_WEIGHTS',str(ROOT.parent/'models'/'yolo11n.pt'))
CONFIDENCE=float(os.getenv('RISK_CONFIDENCE','0.25'))
IOU=float(os.getenv('RISK_IOU','0.45'))
IMG_SIZE=int(os.getenv('RISK_IMG_SIZE','640'))
PERSON_CLASSES={'person'}
HELMET_CLASSES={'helmet','hardhat','hard_hat','safety_helmet'}
VEST_CLASSES={'vest','safety_vest','reflective_vest'}
NO_HELMET_CLASSES={'no_helmet','nohelmet','without_helmet'}
NO_VEST_CLASSES={'no_vest','novest','without_vest'}
FIRE_CLASSES={'fire','flame'}
SMOKE_CLASSES={'smoke'}
FALL_CLASSES={'fall','fallen_person'}
