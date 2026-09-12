from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.reporting import router
app=FastAPI(title='Construction Intelligence Hub — Milestone 4',version='4.1.0',description='Reporting and decision intelligence layer for construction projects.')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(router,prefix='/api/v1')
@app.get('/health')
def health(): return {'status':'ok','milestone':4,'version':'4.1.0'}
@app.exception_handler(Exception)
async def unexpected(_,exc): return JSONResponse(status_code=500,content={'detail':f'Server error: {exc}'})
