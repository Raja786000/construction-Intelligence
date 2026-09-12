from abc import ABC, abstractmethod
from pathlib import Path
import cv2

SEVERITY_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}

class Detector(ABC):
    key = "base"
    category = "base"
    title = "Base detector"
    baseline_threshold = 0.78

    def __init__(self, optional_model_path=None):
        self.optional_model_path = Path(optional_model_path) if optional_model_path else None
        self.external_model_enabled = bool(self.optional_model_path and self.optional_model_path.exists())
        self._yolo = None

    @property
    def engine(self):
        return "External YOLO" if self.external_model_enabled else "Built-in CV baseline"

    def external_findings(self, image_path):
        """Run an optional YOLO model when a category model is present.

        The baseline remains the default so the project runs without model files.
        """
        if not self.external_model_enabled:
            return []
        try:
            from ..models.yolo_adapter import YOLOAdapter
            if self._yolo is None:
                self._yolo = YOLOAdapter(str(self.optional_model_path), threshold=self.baseline_threshold)
            detections = self._yolo.predict(image_path)
        except Exception:
            # A missing optional dependency/model should not break baseline inspection.
            return []

        out = []
        for d in detections:
            conf = float(d.get("confidence", 0))
            if conf < self.baseline_threshold:
                continue
            label = str(d.get("label", self.category)).strip().lower().replace(" ", "_")
            severity = "critical" if conf >= .92 else "high" if conf >= .82 else "medium"
            out.append(finding(
                self.category,
                label or f"{self.category}_defect",
                f"External YOLO model detected {label.replace('_', ' ')}.",
                conf,
                severity,
                "Detection produced by the configured category YOLO model.",
                image_path,
                d.get("bbox"),
                "Verify the detected condition against project drawings, specifications and qualified site inspection.",
                "yolo"
            ))
        return out

    @abstractmethod
    def detect(self, image_path):
        ...

def load_image(path):
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError(f"Could not read image: {path}")
    return image

def clamp_box(x1, y1, x2, y2, w, h):
    x1, y1 = max(0, int(x1)), max(0, int(y1))
    x2, y2 = min(w - 1, int(x2)), min(h - 1, int(y2))
    if x2 <= x1 or y2 <= y1:
        return None
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}

def finding(category, defect_type, description, confidence, severity, evidence,
            image_path, box, action, source):
    return {
        "finding_id": None,
        "inspection_category": category,
        "defect_type": defect_type,
        "description": description,
        "confidence": round(float(confidence), 3),
        "severity": severity,
        "evidence": evidence,
        "image_id": str(image_path),
        "bounding_boxes": [box] if box else [],
        "measurements": {},
        "source_tool": source,
        "requires_human_verification": True,
        "recommended_action": action,
    }
