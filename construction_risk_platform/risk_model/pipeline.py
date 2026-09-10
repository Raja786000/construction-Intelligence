import cv2
from .detector import ConstructionDetector
from .risk_engine import calculate_risk
class RiskPipeline:
    def __init__(self,weights=None): self.detector=ConstructionDetector(weights)
    def analyze_image(self,image,source='image',frame_id=None):
        ds,raw=self.detector.detect(image); return calculate_risk(ds,frame_id,source),raw.plot()
    def analyze_video(self,source=0,display=True,save_path=None,callback=None):
        cap=cv2.VideoCapture(source)
        if not cap.isOpened(): raise RuntimeError(f'Cannot open video source: {source}')
        writer=None; fid=0
        try:
            while True:
                ok,frame=cap.read()
                if not ok: break
                risk,ann=self.analyze_image(frame,str(source),fid)
                if callback: callback(risk.to_dict())
                if save_path and writer is None:
                    h,w=ann.shape[:2]; writer=cv2.VideoWriter(save_path,cv2.VideoWriter_fourcc(*'mp4v'),20,(w,h))
                if writer: writer.write(ann)
                if display:
                    cv2.putText(ann,f'{risk.risk_level} | {risk.risk_score}',(20,40),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
                    cv2.imshow('Construction Risk Monitoring',ann)
                    if cv2.waitKey(1)&0xFF in (27,ord('q')): break
                fid+=1
        finally:
            cap.release()
            if writer: writer.release()
            cv2.destroyAllWindows()
