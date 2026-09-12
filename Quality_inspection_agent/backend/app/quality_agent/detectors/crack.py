import cv2
import numpy as np
from .base import Detector, load_image, clamp_box, finding

class CrackDetector(Detector):
    key = "crack"
    category = "crack"
    title = "Crack detection"
    baseline_threshold = .76

    def detect(self, image_path):
        external = self.external_findings(image_path)
        if external:
            return external
        img = load_image(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # A crack baseline looks for a connected, thin dark feature. This is much
        # less sensitive to ordinary rectangular edges than raw Canny contours.
        smooth = cv2.GaussianBlur(gray, (3, 3), 0)
        mask = cv2.threshold(smooth, 105, 255, cv2.THRESH_BINARY_INV)[1]
        border = max(35, int(min(w, h) * .06))
        mask[:border, :] = 0; mask[-border:, :] = 0
        mask[:, :border] = 0; mask[:, -border:] = 0
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8))

        n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
        best = None
        for i in range(1, n):
            x, y, cw, ch, pixels = stats[i]
            length = max(cw, ch)
            short = max(1, min(cw, ch))
            aspect = length / short
            area_ratio = pixels / float(w*h)
            bbox_ratio = pixels / float(max(1, cw*ch))
            if length < max(80, int(min(w,h)*.14)):
                continue
            if not (2.25 <= aspect <= 9.0):
                continue
            if not (.0015 <= area_ratio <= .08):
                continue
            # Cracks are sparse inside their bounding rectangle. Solid dark
            # objects/doors are therefore rejected.
            if bbox_ratio > .34:
                continue
            score = .68 + min(.16, (aspect-2.25)*.035) + min(.10, length/max(w,h)*.12)
            if bbox_ratio < .10:
                score += .04
            score = min(.97, score)
            if best is None or score > best[0]:
                best = (score, (x,y,x+cw,y+ch))

        if not best or best[0] < self.baseline_threshold:
            return []
        conf, b = best
        severity = "high" if (b[2]-b[0]) > w*.45 else "medium"
        return [finding(
            self.category, "crack",
            "A strong linear feature consistent with a visible crack was detected.",
            conf, severity,
            "Thin connected dark feature passed the crack-shape and sparsity screening rules.",
            image_path, clamp_box(*b, w, h),
            "Have the site engineer verify crack location, width, depth and structural significance.",
            "crack_baseline"
        )]
