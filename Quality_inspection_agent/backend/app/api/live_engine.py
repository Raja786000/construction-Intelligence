from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import numpy as np

from ..services.model_config import MODEL_CONFIG, LIVE_YOLO
from ..quality_agent.models.yolo_adapter import YOLOAdapter
from ..quality_agent.detectors.crack import CrackDetector
from ..quality_agent.detectors.concrete import ConcreteDetector
from ..quality_agent.detectors.surface import SurfaceDetector
from ..quality_agent.detectors.corrosion import CorrosionDetector


# Live mode deliberately does not run the baseline component detector. Generic
# rectangles and clothing are not evidence of an installation defect. A trained
# component YOLO model is used when one is supplied.
BASELINE_DETECTORS = [
    CrackDetector(),
    ConcreteDetector(),
    SurfaceDetector(),
    CorrosionDetector(),
]

LIVE_THRESHOLDS = {
    "crack": 0.80,
    "concrete": 0.84,
    "surface": 0.82,
    "corrosion": 0.84,
    "component": 0.88,
}


class LiveQualityEngine:
    def __init__(self):
        self.global_yolo = YOLOAdapter(LIVE_YOLO, threshold=0.58) if LIVE_YOLO else None
        self.category_models = {}
        for category, path in MODEL_CONFIG.items():
            if Path(path).exists():
                self.category_models[category] = YOLOAdapter(str(path), threshold=LIVE_THRESHOLDS.get(category, 0.65))

        self.face = cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"))
        self.upper = cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / "haarcascade_upperbody.xml"))
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def status(self):
        models = sorted(self.category_models.keys())
        if self.global_yolo and self.global_yolo.enabled:
            mode = "YOLO live model"
        elif models:
            mode = "Category YOLO + live CV"
        else:
            mode = "Enhanced live CV"
        return {
            "enabled": True,
            "mode": mode,
            "yolo_enabled": bool((self.global_yolo and self.global_yolo.enabled) or models),
            "category_models": models,
            "baseline_categories": [d.category for d in BASELINE_DETECTORS],
            "message": "Live inspection is ready. Human regions are suppressed and detections require conservative validation.",
        }

    @staticmethod
    def _clamp_box(b, w, h):
        x1 = max(0, min(w - 1, int(b[0])))
        y1 = max(0, min(h - 1, int(b[1])))
        x2 = max(0, min(w - 1, int(b[2])))
        y2 = max(0, min(h - 1, int(b[3])))
        return {"x1": x1, "y1": y1, "x2": x2, "y2": y2} if x2 > x1 and y2 > y1 else None

    def _human_mask(self, image: np.ndarray) -> Tuple[np.ndarray, List[dict]]:
        """Return a mask of regions belonging to people.

        We suppress faces/upper bodies before quality detectors. This prevents
        skin, hair, shirts and generic clothing texture from becoming crack,
        surface or corrosion candidates. The mask is only a negative ROI; it
        does not classify or report people.
        """
        h, w = image.shape[:2]
        small = cv2.resize(image, (min(640, w), min(640, h)))
        sh, sw = small.shape[:2]
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        scale_x, scale_y = w / sw, h / sh
        boxes = []

        if not self.face.empty():
            faces = self.face.detectMultiScale(gray, scaleFactor=1.12, minNeighbors=6, minSize=(28, 28))
            for x, y, bw, bh in faces:
                roi = small[max(0,y):min(sh,y+bh), max(0,x):min(sw,x+bw)]
                if roi.size == 0:
                    continue
                hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                ycrcb_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2YCrCb)
                skin_hsv = cv2.inRange(hsv_roi, np.array([0, 25, 45]), np.array([25, 230, 255]))
                skin_ycc = cv2.inRange(ycrcb_roi, np.array([0, 133, 77]), np.array([255, 180, 135]))
                skin_ratio = float(np.count_nonzero(cv2.bitwise_and(skin_hsv, skin_ycc))) / float(max(1, roi.shape[0]*roi.shape[1]))
                # Haar can fire on concrete textures. Only mask a face candidate
                # when it also has a plausible skin region.
                if skin_ratio >= 0.10:
                    boxes.append((x * scale_x, y * scale_y, (x + bw) * scale_x, (y + bh) * scale_y, "face"))

        if not self.upper.empty():
            bodies = self.upper.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=5, minSize=(55, 70))
            for x, y, bw, bh in bodies:
                boxes.append((x * scale_x, y * scale_y, (x + bw) * scale_x, (y + bh) * scale_y, "upper_body"))

        # HOG is used only as a second safety net. It is intentionally run on a
        # small frame to keep live latency reasonable.
        try:
            rects, _ = self.hog.detectMultiScale(small, winStride=(8, 8), padding=(8, 8), scale=1.05)
            for x, y, bw, bh in rects:
                boxes.append((x * scale_x, y * scale_y, (x + bw) * scale_x, (y + bh) * scale_y, "person"))
        except Exception:
            pass

        mask = np.zeros((h, w), dtype=np.uint8)
        public_boxes = []
        pad_x = max(12, int(w * 0.015))
        pad_y = max(12, int(h * 0.025))
        for x1, y1, x2, y2, kind in boxes:
            x1, y1 = max(0, int(x1) - pad_x), max(0, int(y1) - pad_y)
            x2, y2 = min(w, int(x2) + pad_x), min(h, int(y2) + pad_y)
            cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
            public_boxes.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2, "type": kind})
        return mask, public_boxes

    @staticmethod
    def _candidate_overlaps_person(box: dict, person_mask: np.ndarray, min_overlap: float = 0.12) -> bool:
        if not box:
            return False
        h, w = person_mask.shape[:2]
        x1 = max(0, min(w - 1, int(box["x1"])))
        y1 = max(0, min(h - 1, int(box["y1"])))
        x2 = max(0, min(w, int(box["x2"])))
        y2 = max(0, min(h, int(box["y2"])))
        if x2 <= x1 or y2 <= y1:
            return False
        roi = person_mask[y1:y2, x1:x2]
        return float(np.count_nonzero(roi)) / float(max(1, roi.size)) >= min_overlap

    def _enhanced_crack(self, image: np.ndarray) -> List[dict]:
        """Adaptive black-hat/Hough crack screen for live lighting.

        Unlike a fixed dark-pixel threshold, this works on light and mid-tone
        concrete. It requires a thin, elongated, low-area feature on a mostly
        neutral surface, which rejects most shirt/face edges.
        """
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        bh = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)))
        p = float(np.percentile(bh, 96.5))
        threshold = max(14.0, min(42.0, p * 0.78))
        mask = cv2.threshold(bh, threshold, 255, cv2.THRESH_BINARY)[1]
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best = None
        for c in contours:
            x, y, cw, ch = cv2.boundingRect(c)
            length = max(cw, ch)
            short = max(1, min(cw, ch))
            aspect = length / short
            area = cv2.contourArea(c)
            ratio = area / float(w * h)
            if length < max(55, int(min(w, h) * 0.09)) or aspect < 4.0 or aspect > 35.0:
                continue
            if ratio < 0.00015 or ratio > 0.025:
                continue
            box = {"x1": x, "y1": y, "x2": x + cw, "y2": y + ch}
            roi_hsv = hsv[y:y+ch, x:x+cw]
            roi_lab = lab[y:y+ch, x:x+cw]
            if roi_hsv.size == 0:
                continue
            saturation = float(roi_hsv[:, :, 1].mean()) / 255.0
            a_channel = float(roi_lab[:, :, 1].mean())
            b_channel = float(roi_lab[:, :, 2].mean())
            # Concrete/plaster is commonly close to neutral. A high-saturation
            # colored ROI is much more likely to be clothing/signage than a crack.
            if saturation > 0.42:
                continue
            # Avoid the strongest global borders and UI-like frame edges.
            margin = max(8, int(min(w, h) * 0.025))
            if x < margin or y < margin or x + cw > w - margin or y + ch > h - margin:
                continue
            local = bh[y:y+ch, x:x+cw]
            strength = float(local.mean()) / 255.0
            score = min(0.97, 0.73 + min(0.13, strength * 0.55) + min(0.09, (aspect / 20.0) * 0.09))
            if score >= LIVE_THRESHOLDS["crack"] and (best is None or score > best[0]):
                best = (score, box)
        if not best:
            return []
        conf, b = best
        severity = "high" if max(b["x2"] - b["x1"], b["y2"] - b["y1"]) > max(w, h) * 0.42 else "medium"
        return [{"label": "crack", "category": "crack", "confidence": round(conf, 3), "severity": severity, "bbox": b}]

    def _enhanced_surface(self, image: np.ndarray) -> List[dict]:
        """Detect a localized finish/texture break while rejecting uniform clothing."""
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        lap = np.abs(cv2.Laplacian(blur, cv2.CV_32F))
        rows, cols = 5, 5
        tiles = []
        for r in range(rows):
            for c in range(cols):
                y1, y2 = r*h//rows, (r+1)*h//rows
                x1, x2 = c*w//cols, (c+1)*w//cols
                roi = lap[y1:y2, x1:x2]
                hsv_roi = hsv[y1:y2, x1:x2]
                tiles.append((float(roi.mean()), float(roi.std()), float(hsv_roi[:, :, 1].mean()) / 255.0, (x1,y1,x2,y2)))
        values = np.array([t[0] for t in tiles], dtype=np.float32)
        baseline = float(np.median(values))
        mad = float(np.median(np.abs(values - baseline))) + 1e-6
        # Camera borders, windows and UI-like frame edges are common sources of
        # texture outliers. Prefer interior tiles for the live finish decision.
        margin = max(1, int(min(h, w) * 0.08))
        eligible = [i for i,t in enumerate(tiles) if t[3][0] >= margin and t[3][1] >= margin and t[3][2] <= w-margin and t[3][3] <= h-margin]
        if not eligible:
            eligible = list(range(len(tiles)))
        idx = max(eligible, key=lambda i: tiles[i][0] + (cv2.Canny(gray,55,135)[tiles[i][3][1]:tiles[i][3][3],tiles[i][3][0]:tiles[i][3][2]].mean()/255.0)*3.0)
        val, std, sat, box = tiles[idx]
        delta = val - baseline
        # Finish anomalies need to be a strong local outlier and reasonably neutral.
        edges = cv2.Canny(gray, 55, 135)
        y1,y2 = box[1],box[3]; x1,x2 = box[0],box[2]
        edge_roi = edges[y1:y2, x1:x2]
        edge_density = float(np.count_nonzero(edge_roi)) / float(max(1,(x2-x1)*(y2-y1)))
        # Reject clean rectangular component/window/frame geometry. Finish damage
        # is more likely to produce irregular or diagonal texture than a set of
        # long axis-aligned borders.
        line_count = 0
        lines = cv2.HoughLinesP(edge_roi, 1, np.pi/180, threshold=28, minLineLength=max(35, int(min(x2-x1,y2-y1)*0.35)), maxLineGap=8)
        if lines is not None:
            for line in lines[:,0]:
                dx, dy = float(line[2]-line[0]), float(line[3]-line[1])
                angle = abs(np.degrees(np.arctan2(dy, dx)))
                angle = min(angle, 180.0-angle)
                if angle < 8.0 or angle > 82.0:
                    line_count += 1
        geometric_border = line_count >= 4
        texture_outlier = delta >= max(10.0, mad * 4.2) and std >= 10.0
        edge_outlier = edge_density >= 0.022 and delta >= max(0.03, mad * 0.10) and std >= 1.5 and not geometric_border
        if (not texture_outlier and not edge_outlier) or sat > 0.42:
            return []
        if val > 85 and sat > 0.30:
            return []
        conf = min(0.96, 0.79 + min(0.10, max(delta, edge_density*100) / 110.0) + min(0.07, std / 240.0))
        if conf < LIVE_THRESHOLDS["surface"]:
            return []
        return [{
            "label": "surface_finish_irregularity",
            "category": "surface",
            "confidence": round(conf, 3),
            "severity": "low",
            "bbox": {"x1": box[0], "y1": box[1], "x2": box[2], "y2": box[3]},
        }]

    def _baseline_path_detections(self, detector, image: np.ndarray, person_mask: np.ndarray):
        fd, path = tempfile.mkstemp(suffix=".jpg")
        os.close(fd)
        try:
            cv2.imwrite(path, image, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
            candidates = detector.detect(path)
            out = []
            threshold = LIVE_THRESHOLDS.get(detector.category, 0.88)
            for f in candidates:
                conf = float(f.get("confidence", 0))
                if conf < threshold:
                    continue
                for b in f.get("bounding_boxes", []):
                    if not b or self._candidate_overlaps_person(b, person_mask, 0.08):
                        continue
                    if detector.category == "corrosion":
                        bw = max(1, int(b["x2"] - b["x1"]))
                        bh = max(1, int(b["y2"] - b["y1"]))
                        aspect = max(bw, bh) / float(min(bw, bh))
                        # Skin and orange clothing often satisfy the HSV rust
                        # range. Compact human-colored blobs are not promoted
                        # to corrosion in live mode. Elongated/irregular rust
                        # remains eligible, especially when it persists in time.
                        if aspect < 2.0:
                            continue
                    out.append({"label": f.get("defect_type", detector.category), "category": detector.category,
                                "confidence": conf, "severity": f.get("severity", "medium"), "bbox": b})
            return out
        finally:
            try: os.remove(path)
            except OSError: pass

    def _validate_yolo(self, detections, width, height, person_mask):
        out = []
        allowed = {"crack", "concrete", "surface", "corrosion", "component"}
        aliases = {
            "cracks": "crack", "rust": "corrosion", "corrosion_or_rust_indicator": "corrosion",
            "concrete_defect": "concrete", "concrete_surface_defect": "concrete",
            "surface_defect": "surface", "surface_finish_irregularity": "surface",
        }
        for d in detections or []:
            raw = str(d.get("label", "")).strip().lower().replace(" ", "_")
            category = aliases.get(raw, raw)
            if category not in allowed:
                continue
            conf = float(d.get("confidence", 0))
            if conf < LIVE_THRESHOLDS.get(category, 0.88):
                continue
            bbox = d.get("bbox") or {}
            if self._candidate_overlaps_person(bbox, person_mask, 0.10):
                continue
            severity = "critical" if conf >= .93 else "high" if conf >= .84 else "medium"
            out.append({"label": raw or category, "category": category, "confidence": round(conf,3), "severity": severity, "bbox": bbox})
        return out

    def analyze(self, image: np.ndarray):
        h, w = image.shape[:2]
        person_mask, _ = self._human_mask(image)
        safe = image.copy()
        safe[person_mask > 0] = cv2.GaussianBlur(safe, (31, 31), 0)[person_mask > 0]

        detections = []
        mode = "Enhanced live CV"

        # A configured trained model always takes priority. If a category model
        # exists, we do not mix its output with a weaker baseline for that category.
        if self.global_yolo and self.global_yolo.enabled:
            mode = "YOLO live model"
            detections.extend(self._validate_yolo(self.global_yolo.predict(safe), w, h, person_mask))
        else:
            for d in BASELINE_DETECTORS:
                model = self.category_models.get(d.category)
                if model and model.enabled:
                    mode = "Category YOLO + live CV"
                    detections.extend(self._validate_yolo(model.predict(safe), w, h, person_mask))
                    continue
                if d.category == "crack":
                    # Adaptive live detector first, then the existing crack detector
                    # which is particularly good on the supplied construction sample.
                    detections.extend(self._enhanced_crack(safe))
                    detections.extend(self._baseline_path_detections(d, safe, person_mask))
                elif d.category == "surface":
                    detections.extend(self._enhanced_surface(safe))
                    detections.extend(self._baseline_path_detections(d, safe, person_mask))
                else:
                    detections.extend(self._baseline_path_detections(d, safe, person_mask))

        # Deduplicate overlapping boxes of the same category/label.
        detections = self._dedupe(detections)
        return detections, mode, person_mask

    @staticmethod
    def _iou(a, b):
        x1=max(a["x1"],b["x1"]); y1=max(a["y1"],b["y1"])
        x2=min(a["x2"],b["x2"]); y2=min(a["y2"],b["y2"])
        inter=max(0,x2-x1)*max(0,y2-y1)
        aa=max(1,(a["x2"]-a["x1"])*(a["y2"]-a["y1"]))
        ab=max(1,(b["x2"]-b["x1"])*(b["y2"]-b["y1"]))
        return inter/max(1,aa+ab-inter)

    def _dedupe(self, detections):
        result=[]
        for d in sorted(detections, key=lambda x: x.get("confidence",0), reverse=True):
            if any(d["category"]==r["category"] and self._iou(d["bbox"],r["bbox"])>.45 for r in result):
                continue
            result.append(d)
        return result[:12]
