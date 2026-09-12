from pathlib import Path

class YOLOAdapter:
    def __init__(self,path,threshold=.45):
        self.path=Path(path) if path else Path("")
        self.threshold=threshold
        self.model=None

    @property
    def enabled(self):
        return bool(str(self.path)) and self.path.exists()

    def predict(self,image):
        if not self.enabled:
            return []
        if self.model is None:
            from ultralytics import YOLO
            self.model=YOLO(str(self.path))
        result=self.model.predict(source=image,conf=self.threshold,verbose=False)[0]
        out=[]
        if result.boxes is None:
            return out
        for box in result.boxes:
            xyxy=box.xyxy[0].tolist()
            conf=float(box.conf[0]); cls_id=int(box.cls[0])
            out.append({
                "label":str(result.names[cls_id]),
                "confidence":conf,
                "bbox":{
                    "x1":float(xyxy[0]),"y1":float(xyxy[1]),
                    "x2":float(xyxy[2]),"y2":float(xyxy[3])
                }
            })
        return out
