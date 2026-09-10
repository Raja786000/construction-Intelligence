from pathlib import Path
from ultralytics import YOLO
from . import config
from .schemas import Detection
class ConstructionDetector:
    def __init__(self,weights=None):
        self.weights_path=Path(weights or config.MODEL_WEIGHTS)
        if not self.weights_path.exists(): raise FileNotFoundError(f'YOLO weights not found: {self.weights_path}')
        self.model=YOLO(str(self.weights_path))
    @property
    def class_names(self):
        n=self.model.names
        return n if isinstance(n,dict) else dict(enumerate(n))
    def detect(self,image):
        r=self.model.predict(source=image,conf=config.CONFIDENCE,iou=config.IOU,imgsz=config.IMG_SIZE,verbose=False)[0]
        out=[]
        if r.boxes is None: return out,r
        for b in r.boxes:
            cid=int(b.cls[0].item()); conf=float(b.conf[0].item())
            out.append(Detection(str(self.class_names.get(cid,cid)).lower().strip(),round(conf,3),[int(x) for x in b.xyxy[0].tolist()]))
        return out,r
