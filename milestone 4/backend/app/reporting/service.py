from pathlib import Path
from datetime import datetime, timezone
import csv,json,uuid,re
from app.reporting.store import EventStore
from app.reporting.aggregator import aggregate
from app.reporting.pdf import build_pdf
BASE=Path(__file__).resolve().parents[2]
class ReportingService:
    def __init__(self): self.store=EventStore(); self.report_dir=BASE/'generated_reports'; self.report_dir.mkdir(exist_ok=True)
    def capabilities(self): return {'version':'4.1.0','expected_agents':['quality','safety','compliance','schedule','cost','weather','resource'],'features':['persistent projects','project switcher','dashboard','normalized agent intake','templates','batch JSON','risk register','agent health','PDF/JSON/CSV reports','responsive enterprise UI']}
    def create_project(self,p):
        pid=p['project_id'].strip();
        if self.store.project(pid): raise ValueError(f"Project '{pid}' already exists. Choose a different Project ID or open the existing project.")
        if not p['name'].strip() or not p['site_id'].strip(): raise ValueError('Project name and Site ID are required.')
        return {'created':True,'project':self.store.create_project({**p,'project_id':pid,'name':p['name'].strip(),'site_id':p['site_id'].strip()})}
    def project(self,pid): return self.store.project(pid)
    def projects(self): return {'projects':self.store.projects()}
    def delete_project(self,pid): self.store.delete_project(pid); return {'deleted':True,'project_id':pid}
    def ingest_event(self,e):
        e=dict(e); e['project_id']=e.get('project_id','').strip(); e['timestamp']=e.get('timestamp') or datetime.now(timezone.utc).isoformat(); e['findings']=e.get('findings') or []; e['findings_count']=len(e['findings']); e['agent']=e.get('agent','').strip().lower()
        if not e['project_id'] or not e['agent']: raise ValueError('Project and agent are required.')
        return {'accepted':True,'event':self.store.add(e)}
    def ingest_batch(self,events):
        if not events: raise ValueError('No events supplied.')
        accepted=0
        for e in events: self.ingest_event(e); accepted+=1
        return {'accepted':True,'count':accepted}
    def load_demo(self):
        pid='PROJECT-001'
        if not self.store.project(pid): self.store.create_project({'project_id':pid,'name':'Downtown Commercial Tower','site_id':'SITE-A','project_type':'commercial','location':'Bengaluru, India','owner':'Demo Owner','manager':'Demo PM'})
        if self.store.for_project(pid): return {'accepted':True,'project_id':pid,'events_added':0,'message':'Demo project already loaded.'}
        demo=[('quality','quality_inspection_completed','REVIEW_REQUIRED','HIGH',82,[('HIGH','Concrete surface defect','Localized surface anomaly requires site verification.')]),('safety','safety_inspection_completed','ACTION_REQUIRED','CRITICAL',68,[('CRITICAL','Worker PPE risk','Required protective equipment was not confidently visible.'),('HIGH','Unsafe work-zone condition','Potential hazard detected in work area.')]),('compliance','compliance_inspection_completed','PASS','NONE',100,[]),('schedule','schedule_review_completed','REVIEW_REQUIRED','MEDIUM',91,[('MEDIUM','Milestone variance','A scheduled activity is trending behind baseline.')]),('cost','cost_review_completed','PASS','LOW',96,[('LOW','Minor cost variance','Current variance is within early-warning range.')]),('weather','weather_risk_completed','WARNING','MEDIUM',94,[('MEDIUM','Weather watch','Weather conditions may affect exposed work.')]),('resource','resource_review_completed','PASS','NONE',97,[])]
        for a,et,st,sev,score,fs in demo:
            self.ingest_event({'project_id':pid,'site_id':'SITE-A','agent':a,'event_type':et,'status':st,'severity':sev,'score':score,'findings':[{'severity':s,'title':t,'description':d,'recommended_action':'Review and close the corrective action.'} for s,t,d in fs],'recommendations':['Review open actions and update the project register.'] if fs else []})
        return {'accepted':True,'project_id':pid,'events_added':7,'message':'Demo project loaded.'}
    def dashboard(self,req):
        pid=(req.get('project_id') or '').strip(); p=self.project(pid) if pid else None
        if pid and not p: raise ValueError(f"Project '{pid}' was not found.")
        events=self.store.for_project(pid) if pid else []
        s=aggregate(pid,events)
        return {'project_id':pid,'project':p,'projects':self.store.projects(),'summary':s,'recent_events':events[-20:][::-1]}
    def project_events(self,pid): return {'project_id':pid,'events':self.store.for_project(pid)}
    def create_report(self,req):
        pid=req['project_id']; events=self.store.for_project(pid)
        if not events: raise ValueError('No agent events exist for this project. Add data from Data Intake first.')
        data=aggregate(pid,events); rid=uuid.uuid4().hex[:10]; safe_pid=re.sub(r'[^A-Za-z0-9_-]','_',pid); base=f'construction_intelligence_{safe_pid}_{rid}'
        pdf=self.report_dir/(base+'.pdf'); js=self.report_dir/(base+'.json'); cp=self.report_dir/(base+'.csv'); build_pdf(pdf,data,req.get('report_type','executive'))
        js.write_text(json.dumps({'report_id':rid,'report_type':req.get('report_type','executive'),'generated_at':datetime.now(timezone.utc).isoformat(),'project':self.project(pid),'summary':data,'events':events if req.get('include_events',True) else []},indent=2),encoding='utf-8')
        with cp.open('w',newline='',encoding='utf-8') as fh:
            w=csv.writer(fh); w.writerow(['priority','agent','severity','title','description','recommended_action','source_event','timestamp'])
            for i,f in enumerate(sorted(data['findings'],key=lambda x:{'CRITICAL':0,'HIGH':1,'MEDIUM':2,'LOW':3,'NONE':4}.get(x['severity'],5)),1): w.writerow([i,f['agent'],f['severity'],f['title'],f['description'],f['recommended_action'],f['source_event'],f['timestamp']])
        return {'report_id':rid,'project_id':pid,'report_type':req.get('report_type','executive'),'summary':data,'downloads':{'pdf':f'/api/v1/reporting/download/{pdf.name}','json':f'/api/v1/reporting/download/{js.name}','csv':f'/api/v1/reporting/download/{cp.name}'}}
    def reports(self,project_id=''):
        out=[]
        for p in sorted(self.report_dir.glob('*.pdf'),key=lambda x:x.stat().st_mtime,reverse=True):
            if project_id and f'_{re.sub(r"[^A-Za-z0-9_-]","_",project_id)}_' not in p.name: continue
            stem=p.stem; out.append({'filename':p.name,'created_at':datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),'pdf':f'/api/v1/reporting/download/{p.name}','json':f'/api/v1/reporting/download/{stem}.json','csv':f'/api/v1/reporting/download/{stem}.csv'})
        return {'reports':out[:50]}
