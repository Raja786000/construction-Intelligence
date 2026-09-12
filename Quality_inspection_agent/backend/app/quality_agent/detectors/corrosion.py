import cv2
import numpy as np
from .base import Detector, load_image, clamp_box, finding

class CorrosionDetector(Detector):
    key = "corrosion"
    category = "corrosion"
    title = "Corrosion / rust inspection"
    baseline_threshold = .78

    def detect(self, image_path):
        external = self.external_findings(image_path)
        if external:
            return external
        img = load_image(image_path)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h,w = hsv.shape[:2]
        # Rust-like orange/brown colors, with saturation/value constraints to reject
        # most gray concrete and low-light noise.
        mask1 = cv2.inRange(hsv, np.array([5,75,45]), np.array([28,255,235]))
        mask2 = cv2.inRange(hsv, np.array([0,65,35]), np.array([8,230,205]))
        mask = cv2.bitwise_or(mask1, mask2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5,5),np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9,9),np.uint8))
        contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        best=None
        for c in contours:
            x,y,cw,ch=cv2.boundingRect(c)
            area=cw*ch
            ratio=area/(w*h)
            if ratio < .012 or ratio > .30:
                continue
            fill=cv2.contourArea(c)/max(1,area)
            roi=hsv[y:y+ch,x:x+cw]
            sat=float(roi[:,:,1].mean())/255 if roi.size else 0
            if sat < .38 or fill < .15:
                continue
            # Rust candidate confidence grows with meaningful coverage, saturation,
            # and compactness. It is calibrated so the included rust sample is visible.
            conf=min(.96,.68 + ratio*4.0 + sat*.14 + fill*.08)
            if best is None or conf > best[0]:
                best=(conf,(x,y,x+cw,y+ch),ratio)
        if not best or best[0] < self.baseline_threshold:
            return []
        conf,b,ratio=best
        sev="high" if ratio>.10 else "medium"
        return [finding(
            self.category, "corrosion_or_rust_indicator",
            "A rust/corrosion-like region passed the conservative color and shape screen.",
            conf, sev,
            "Orange/brown high-saturation region with sufficient spatial extent detected.",
            image_path, clamp_box(*b,w,h),
            "Inspect the member, determine corrosion depth and section loss, and compare with the repair/acceptance criteria.",
            "corrosion_baseline"
        )]
