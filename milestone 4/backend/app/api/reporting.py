from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.schemas import AgentEvent,DashboardRequest,ProjectCreate,ReportRequest
from app.reporting.service import ReportingService
router=APIRouter(prefix='/reporting',tags=['Reporting Intelligence']); service=ReportingService()
def safe(fn):
    try: return fn()
    except ValueError as e: raise HTTPException(status_code=400,detail=str(e))
@router.get('/capabilities')
def capabilities(): return service.capabilities()
@router.post('/projects')
def create_project(req:ProjectCreate): return safe(lambda:service.create_project(req.model_dump()))
@router.get('/projects')
def projects(): return service.projects()
@router.get('/projects/{project_id}')
def project(project_id:str):
    p=service.project(project_id)
    if not p: raise HTTPException(404,'Project not found')
    return p
@router.delete('/projects/{project_id}')
def delete_project(project_id:str): return service.delete_project(project_id)
@router.post('/events')
def events(e:AgentEvent): return safe(lambda:service.ingest_event(e.model_dump()))
@router.post('/events/batch')
def batch(events:list[AgentEvent]): return safe(lambda:service.ingest_batch([e.model_dump() for e in events]))
@router.post('/demo')
def demo(): return safe(service.load_demo)
@router.post('/dashboard')
def dashboard(req:DashboardRequest): return safe(lambda:service.dashboard(req.model_dump()))
@router.get('/project/{project_id}/events')
def project_events(project_id:str): return service.project_events(project_id)
@router.post('/report')
def report(req:ReportRequest): return safe(lambda:service.create_report(req.model_dump()))
@router.get('/reports')
def reports(project_id:str=''): return service.reports(project_id)
@router.get('/download/{filename}')
def download(filename:str):
    p=Path(service.report_dir)/Path(filename).name
    if not p.exists(): raise HTTPException(404,'Report not found')
    return FileResponse(str(p),filename=p.name)
