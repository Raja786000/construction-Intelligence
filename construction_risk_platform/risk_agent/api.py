from fastapi import FastAPI,UploadFile,File,HTTPException
import cv2,numpy as np
from .agent import ConstructionRiskAgent
app=FastAPI(title='Construction Risk Agent'); agent=ConstructionRiskAgent()
@app.get('/health')
def health(): return {'status':'ok','service':'risk-agent'}
@app.post('/agent/analyze')
async def analyze(file:UploadFile=File(...)):
 data=await file.read(); im=cv2.imdecode(np.frombuffer(data,np.uint8),cv2.IMREAD_COLOR)
 if im is None: raise HTTPException(400,'Invalid image')
 risk,_=agent.analyze_frame(im,file.filename or 'upload'); return risk
