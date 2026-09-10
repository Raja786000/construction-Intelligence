from dataclasses import dataclass,asdict
@dataclass
class Detection:
    class_name:str; confidence:float; bbox:list[int]
    def to_dict(self): return asdict(self)
@dataclass
class RiskResult:
    risk_score:float; risk_level:str; reasons:list[str]; detections:list[dict]; frame_id:int|None=None; source:str|None=None
    def to_dict(self): return asdict(self)
