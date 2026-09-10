from fastapi import FastAPI,UploadFile,File,HTTPException
import cv2,numpy as np
from .pipeline import RiskPipeline
app=FastAPI(title='Construction Risk Model API'); pipeline=RiskPipeline()
@app.get('/health')
def health(): return {'status':'ok','model':str(pipeline.detector.weights_path)}
@app.post('/predict/image')
async def predict_image(file:UploadFile=File(...)):
 data=await file.read(); im=cv2.imdecode(np.frombuffer(data,np.uint8),cv2.IMREAD_COLOR)
 if im is None: raise HTTPException(400,'Invalid image')
 risk,_=pipeline.analyze_image(im,file.filename or 'upload'); return risk.to_dict()
