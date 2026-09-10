from risk_model.pipeline import RiskPipeline
from .alerts import AlertManager
class ConstructionRiskAgent:
 def __init__(self,weights=None): self.pipeline=RiskPipeline(weights); self.alerts=AlertManager()
 def analyze_frame(self,frame,source='live'):
  risk,ann=self.pipeline.analyze_image(frame,source); d=risk.to_dict(); self.alerts.send(d); return d,ann
 def monitor(self,source=0,save_path=None): self.pipeline.analyze_video(source,True,save_path,self.alerts.send)
