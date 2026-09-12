import cv2
import numpy as np
from .base import Detector, load_image, clamp_box, finding

class SurfaceDetector(Detector):
    key = "surface"
    category = "surface"
    title = "Surface / finish inspection"
    baseline_threshold = .84

    def detect(self, image_path):
        external = self.external_findings(image_path)
        if external:
            return external
        img = load_image(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        lap = cv2.Laplacian(cv2.GaussianBlur(gray, (3,3), 0), cv2.CV_64F)
        mag = np.abs(lap)
        rows, cols = 4, 4
        tiles = []
        for r in range(rows):
            for c in range(cols):
                y1,y2 = r*h//rows,(r+1)*h//rows
                x1,x2 = c*w//cols,(c+1)*w//cols
                roi = mag[y1:y2,x1:x2]
                tiles.append((float(roi.mean()), float(roi.std()), (x1,y1,x2,y2)))
        values = np.array([x[0] for x in tiles])
        baseline = float(np.median(values))
        spread = float(np.median(np.abs(values - baseline))) + 1e-6
        idx = int(np.argmax(values))
        val, std, box = tiles[idx]
        delta = val - baseline
        # A finish anomaly needs a substantial local outlier, not merely texture variation.
        if delta < max(18.0, spread * 3.5) or std < 12:
            return []
        conf = min(.95, .70 + min(.20, delta / 120) + min(.08, std / 220))
        if conf < self.baseline_threshold:
            return []
        return [finding(
            self.category, "surface_finish_irregularity",
            "A localized surface/finish irregularity passed the conservative visual screen.",
            conf, "low",
            "The region is a strong local texture outlier relative to neighboring surface tiles.",
            image_path, clamp_box(*box,w,h),
            "Review the finish and determine whether patching, grinding, repainting or rework is required.",
            "surface_baseline"
        )]
