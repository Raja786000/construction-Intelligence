from . import config
from .schemas import RiskResult
def calculate_risk(ds,frame_id=None,source=None):
    score=0.; reasons=[]
    def has(names): return any(d.class_name in names for d in ds)
    persons=sum(d.class_name in config.PERSON_CLASSES for d in ds)
    if has(config.FIRE_CLASSES): score+=55; reasons.append('Fire detected')
    if has(config.SMOKE_CLASSES): score+=35; reasons.append('Smoke detected')
    if has(config.FALL_CLASSES): score+=45; reasons.append('Possible fallen worker detected')
    if has(config.NO_HELMET_CLASSES): score+=25; reasons.append('Worker without helmet detected')
    if has(config.NO_VEST_CLASSES): score+=20; reasons.append('Worker without safety vest detected')
    if persons>=5: score+=10; reasons.append('High worker density')
    if persons>=10: score+=15; reasons.append('Very high worker density')
    score=min(100,score)
    level='CRITICAL' if score>=70 else 'HIGH' if score>=45 else 'MEDIUM' if score>=20 else 'LOW'
    if not reasons: reasons=['No configured high-risk condition detected']
    return RiskResult(round(score,1),level,reasons,[d.to_dict() for d in ds],frame_id,source)
