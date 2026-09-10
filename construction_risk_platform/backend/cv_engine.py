import cv2
import numpy as np
import base64
import random
from typing import Dict, List, Any, Tuple
from pathlib import Path
from .config import MODEL_WEIGHTS, CONFIDENCE_THRESHOLD, CLASSES

class ComputerVisionSafetyDetector:
    def __init__(self, weights_path: str = None):
        self.weights_path = Path(weights_path or MODEL_WEIGHTS)
        self.use_yolo = False
        self.model = None

        if self.weights_path.exists():
            try:
                from ultralytics import YOLO
                self.model = YOLO(str(self.weights_path))
                self.use_yolo = True
                print(f"[CV Engine] Loaded PyTorch YOLO weights from {self.weights_path}")
            except Exception as e:
                print(f"[CV Engine] YOLO load fallback to simulation: {e}")

    def analyze_image_file(self, image_bytes: bytes, filename: str = "image.jpg") -> Dict[str, Any]:
        # Decode image
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            # Fallback blank image
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(img, "Sample Construction Feed", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        h, w, _ = img.shape
        detections = []
        violations = []

        if self.use_yolo and self.model is not None:
            results = self.model.predict(source=img, conf=CONFIDENCE_THRESHOLD, verbose=False)[0]
            if results.boxes is not None:
                for b in results.boxes:
                    cid = int(b.cls[0].item())
                    conf = float(b.conf[0].item())
                    bbox = [int(x) for x in b.xyxy[0].tolist()]
                    label = self.model.names.get(cid, str(cid)).lower()
                    detections.append({
                        "class_name": label,
                        "confidence": round(conf, 3),
                        "bbox": bbox
                    })
        else:
            # Simulated Computer Vision Detections tailored for Kaggle / Roboflow PPE datasets
            detections = self._generate_simulated_detections(w, h, filename)

        # Process violations & calculate safety compliance score
        total_workers = sum(1 for d in detections if d["class_name"] in ["person", "hardhat", "no-hardhat", "vest", "no-vest"])
        total_workers = max(1, total_workers)

        no_hardhat_count = sum(1 for d in detections if d["class_name"] == "no-hardhat")
        no_vest_count = sum(1 for d in detections if d["class_name"] == "no-vest")
        fire_count = sum(1 for d in detections if d["class_name"] in ["fire", "smoke"])

        if no_hardhat_count > 0:
            violations.append(f"Detected {no_hardhat_count} worker(s) WITHOUT protective Hardhat")
        if no_vest_count > 0:
            violations.append(f"Detected {no_vest_count} worker(s) WITHOUT High-Visibility Safety Vest")
        if fire_count > 0:
            violations.append(f"CRITICAL HAZARD: Fire or Smoke detected on construction site!")

        # Safety Compliance Score (0 - 100%)
        penalty = (no_hardhat_count * 25) + (no_vest_count * 20) + (fire_count * 50)
        safety_score = max(0.0, min(100.0, 100.0 - penalty))

        risk_level = "CRITICAL" if safety_score < 40 or fire_count > 0 else "HIGH" if safety_score < 65 else "MEDIUM" if safety_score < 85 else "LOW"

        # Draw annotations on image frame
        annotated_img = self._annotate_frame(img, detections)
        _, buffer = cv2.imencode('.jpg', annotated_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        return {
            "filename": filename,
            "safety_score": round(safety_score, 1),
            "risk_level": risk_level,
            "violations_detected": len(violations) > 0,
            "violations": violations,
            "detections": detections,
            "worker_count": total_workers,
            "annotated_image_base64": f"data:image/jpeg;base64,{img_base64}"
        }

    def _generate_simulated_detections(self, width: int, height: int, filename: str) -> List[Dict[str, Any]]:
        # Deterministic simulation based on filename string hash
        seed_val = sum(ord(c) for c in filename)
        rng = random.Random(seed_val)

        dets = []
        # Worker 1
        x1, y1 = int(width * 0.15), int(height * 0.25)
        x2, y2 = int(width * 0.45), int(height * 0.85)
        dets.append({"class_name": "person", "confidence": 0.94, "bbox": [x1, y1, x2, y2]})

        # Hardhat detection or non-compliance
        if seed_val % 2 == 0:
            dets.append({"class_name": "hardhat", "confidence": 0.91, "bbox": [x1+20, y1, x1+120, y1+60]})
        else:
            dets.append({"class_name": "no-hardhat", "confidence": 0.88, "bbox": [x1+20, y1, x1+120, y1+60]})

        # Safety Vest detection
        if seed_val % 3 != 0:
            dets.append({"class_name": "vest", "confidence": 0.89, "bbox": [x1+10, y1+65, x2-10, y1+220]})
        else:
            dets.append({"class_name": "no-vest", "confidence": 0.86, "bbox": [x1+10, y1+65, x2-10, y1+220]})

        # Worker 2
        x3, y3 = int(width * 0.55), int(height * 0.30)
        x4, y4 = int(width * 0.85), int(height * 0.88)
        dets.append({"class_name": "person", "confidence": 0.92, "bbox": [x3, y3, x4, y4]})
        dets.append({"class_name": "hardhat", "confidence": 0.95, "bbox": [x3+15, y3, x3+110, y3+55]})
        dets.append({"class_name": "harness", "confidence": 0.87, "bbox": [x3+20, y3+60, x4-20, y4-40]})

        return dets

    def _annotate_frame(self, img: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        output = img.copy()
        for d in detections:
            bbox = d["bbox"]
            label = d["class_name"]
            conf = d["confidence"]

            # Color coding
            if "no-" in label or label in ["fire", "smoke"]:
                color = (0, 0, 255) # Red for violations
            elif label in ["hardhat", "vest", "harness"]:
                color = (0, 255, 0) # Green for PPE compliance
            else:
                color = (255, 191, 0) # Cyan/Yellow for workers & machinery

            cv2.rectangle(output, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            caption = f"{label.upper()} {int(conf*100)}%"
            cv2.putText(output, caption, (bbox[0], max(20, bbox[1] - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return output
