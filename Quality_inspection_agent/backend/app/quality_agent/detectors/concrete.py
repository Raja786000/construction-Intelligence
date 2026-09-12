import cv2
import numpy as np
from .base import Detector, load_image, clamp_box, finding

class ConcreteDetector(Detector):
    key = "concrete"
    category = "concrete"
    title = "Concrete defect detection"
    baseline_threshold = .80

    def detect(self, image_path):
        external = self.external_findings(image_path)
        if external:
            return external
        img = load_image(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Conservative search for compact, high-contrast void-like regions.
        # It is intended as a prototype screen for obvious honeycombing/voids,
        # not as a substitute for a trained defect detector.
        smooth = cv2.GaussianBlur(gray, (7,7), 0)
        mask = cv2.threshold(smooth, 100, 255, cv2.THRESH_BINARY_INV)[1]
        border = max(35, int(min(w,h)*.06))
        mask[:border,:]=0; mask[-border:,:]=0; mask[:,:border]=0; mask[:,-border:]=0
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5,5),np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9,9),np.uint8))
        contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        best=None
        for c in contours:
            x,y,cw,ch=cv2.boundingRect(c)
            pixels=cv2.contourArea(c)
            area_ratio=pixels/(w*h)
            if not (.008 <= area_ratio <= .09):
                continue
            box_area=max(1,cw*ch)
            fill=pixels/box_area
            perimeter=cv2.arcLength(c,True)
            circularity=(4*np.pi*pixels)/(perimeter*perimeter) if perimeter else 0
            if fill < .25 or circularity < .18:
                continue
            roi=gray[y:y+ch,x:x+cw]
            hsv_roi=hsv[y:y+ch,x:x+cw]
            mean_sat=float(hsv_roi[:,:,1].mean())/255 if hsv_roi.size else 1
            if mean_sat > .30:
                continue
            local_mean=float(roi.mean()) if roi.size else 255
            # Candidate must be materially darker than a dilated neighborhood.
            pad=20
            xa,xb=max(0,x-pad),min(w,x+cw+pad); ya,yb=max(0,y-pad),min(h,y+ch+pad)
            neighborhood=float(gray[ya:yb,xa:xb].mean()) if gray[ya:yb,xa:xb].size else local_mean
            contrast=max(0, neighborhood-local_mean)/255
            score=.64 + min(.18, contrast*1.5) + min(.10, fill*.16) + min(.06,circularity*.08)
            if score < self.baseline_threshold:
                continue
            if best is None or score>best[0]: best=(min(.97,score),(x,y,x+cw,y+ch))
        if not best:
            return []
        conf,b=best
        return [finding(
            self.category,"concrete_surface_defect",
            "A localized high-contrast concrete anomaly passed the conservative visual screen.",
            conf,"medium",
            "Compact void-like region is materially darker than its local surrounding area.",
            image_path,clamp_box(*b,w,h),
            "Inspect the area for honeycombing, voids, spalling or poor consolidation and compare with specifications.",
            "concrete_baseline"
        )]
