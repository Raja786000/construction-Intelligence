import json,time,urllib.request
from datetime import datetime,timezone
from . import config
class AlertManager:
 def __init__(self): self.last={}
 def send(self,risk):
  score=float(risk['risk_score'])
  if score<config.HIGH_RISK_THRESHOLD:return False
  key='|'.join([risk['risk_level']]+risk.get('reasons',[])); now=time.time()
  if now-self.last.get(key,0)<config.ALERT_COOLDOWN_SECONDS:return False
  self.last[key]=now
  payload={'timestamp':datetime.now(timezone.utc).isoformat(),'alert':True,**risk}
  print('\n'+'='*60); print(f"🚨 {risk['risk_level']} CONSTRUCTION RISK ALERT"); print(f"Risk score: {score}"); [print('- '+x) for x in risk.get('reasons',[])]; print('='*60+'\n')
  if config.WEBHOOK_URL:
   try:
    req=urllib.request.Request(config.WEBHOOK_URL,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'},method='POST'); urllib.request.urlopen(req,timeout=5).read()
   except Exception as e: print('Webhook alert failed:',e)
  return True
