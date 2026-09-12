import React,{useState} from "react";
import{createRoot}from"react-dom/client";
import{ShieldCheck,UploadCloud,FileCheck2,AlertTriangle,CheckCircle2,Clock3,FileWarning,ChevronRight,X,RotateCcw,Search,Building2,CalendarDays}from"lucide-react";
import"./style.css";

const API="/api/v1/compliance";
const TYPES=[
 ["permit","Construction permit","Planning/building authorization"],
 ["license","Contractor/license registration","Contractor or trade authorization"],
 ["insurance","Project insurance","General liability / project cover"],
 ["workers_compensation","Workers compensation","Worker injury coverage"],
 ["inspection_certificate","Inspection certificate","Authority / third-party inspection"],
 ["completion_certificate","Completion / occupancy","Completion or occupancy evidence"],
 ["method_statement","Method statement / SWMS","Approved work method"],
 ["risk_assessment","Risk assessment / JHA","Hazard/risk control record"],
 ["environmental_permit","Environmental permit","Environmental approval"],
 ["material_certificate","Material / test certificate","Product or material compliance"]
];

const PRESETS={
 commercial:["permit","license","insurance","inspection_certificate"],
 industrial:["permit","license","insurance","workers_compensation","inspection_certificate","risk_assessment","environmental_permit"],
 residential:["permit","license","insurance","inspection_certificate"],
 infrastructure:["permit","license","insurance","workers_compensation","inspection_certificate","material_certificate","environmental_permit"]
};

function Header({activeTab="compliance",onTab,onNew}){return <header><div className="brand"><div className="logo">CI</div><div><strong>Construction Intelligence Hub</strong><span>Compliance & Insurance Intelligence</span></div></div><nav>{[["compliance","Compliance"],["register","Document Register"],["insurance","Insurance"]].map(([id,label])=><button type="button" key={id} className={activeTab===id?"active":""} onClick={()=>onTab?.(id)}>{label}</button>)}</nav><div className="right"><i/>Agent online{onNew&&<button type="button" className="new" onClick={onNew}><RotateCcw size={14}/> New review</button>}</div></header>}

function App(){
 const blank={project_id:"",site_id:"",project_name:"",jurisdiction:"",inspection_date:new Date().toISOString().slice(0,10),project_type:"commercial",notes:"",required:PRESETS.commercial,coverages:["General Liability"],minimum:"",renewal:"30"};
 const [x,setX]=useState(blank),[files,setFiles]=useState([]),[r,setR]=useState(null),[busy,setBusy]=useState(false),[err,setErr]=useState(""),[activeTab,setActiveTab]=useState("compliance");
 const set=(k,v)=>setX(a=>({...a,[k]:v}));
 const toggle=(k,id)=>setX(a=>({...a,[k]:a[k].includes(id)?a[k].filter(v=>v!==id):[...a[k],id]}));
 const preset=(v)=>setX(a=>({...a,project_type:v,required:PRESETS[v]||[]}));
 const addFiles=(incoming)=>setFiles(current=>[...current,...incoming.filter(file=>!current.some(existing=>existing.name===file.name&&existing.size===file.size))]);
 const removeFile=(index)=>setFiles(current=>current.filter((_,fileIndex)=>fileIndex!==index));
 async function run(){
   setBusy(true);setErr("");setR(null);
   try{
     const fd=new FormData();
    [["project_id",x.project_id.trim()||"UNSPECIFIED-PROJECT"],["site_id",x.site_id],["project_name",x.project_name],["jurisdiction",x.jurisdiction],["inspection_date",x.inspection_date],["project_type",x.project_type],["notes",x.notes],["required_documents",JSON.stringify(x.required)],["required_coverages",JSON.stringify(x.coverages)],["minimum_liability_limit",x.minimum],["renewal_window_days",x.renewal]].forEach(([k,v])=>fd.append(k,v));
     files.forEach(f=>fd.append("files",f));
     const q=await fetch(API+"/inspect",{method:"POST",body:fd}),z=await q.json();
     if(!q.ok)throw Error(z.detail||"Screening failed");setR(z);
   }catch(e){setErr(e.message)}finally{setBusy(false)}
 }
 function reset(){setX(blank);setFiles([]);setR(null);setErr("")}
 if(r)return <>{activeTab==="compliance"?<Results r={r} onNew={reset} onTab={setActiveTab}/>:<ReviewTab tab={activeTab} r={r} files={files} state={x} onFilesChange={addFiles} onFileRemove={removeFile} onStateChange={set} onTab={setActiveTab} onNew={reset}/>}</>;
 if(activeTab!=="compliance")return <><Header activeTab={activeTab} onTab={setActiveTab}/><main><WorkspaceTab tab={activeTab} files={files} state={x} onFilesChange={addFiles} onFileRemove={removeFile} onStateChange={set} onTab={setActiveTab}/></main><footer>Preliminary screening only · Compliance, legal and insurance decisions require qualified human verification.</footer></>;
 return <><Header activeTab={activeTab} onTab={setActiveTab}/><main>
  <section className="hero"><div><p className="eyebrow">MILESTONE 3 · COMPLIANCE & INSURANCE</p><h1>Compliance Intelligence</h1><p>Turn project records into a structured compliance view with document recognition, validity screening and insurance checks.</p></div><div className="statusCard"><ShieldCheck size={25}/><b>Baseline engine ready</b><span>Documents + rules + LangGraph</span></div></section>

  <div className="step"><b>01</b><div><h2>Project profile</h2><span>Tell the agent what it is reviewing.</span></div></div>
  <section className="card"><div className="fields">
   <Field label="Project ID" value={x.project_id} onChange={v=>set("project_id",v)} placeholder="PROJECT-001"/>
   <Field label="Site ID" value={x.site_id} onChange={v=>set("site_id",v)} placeholder="SITE-A"/>
   <Field label="Project name" value={x.project_name} onChange={v=>set("project_name",v)} placeholder="Riverside Commercial Building"/>
   <Field label="Jurisdiction / authority" value={x.jurisdiction} onChange={v=>set("jurisdiction",v)} placeholder="City / State / Authority"/>
   <label className="field"><span>Project type</span><select value={x.project_type} onChange={e=>preset(e.target.value)}>{Object.keys(PRESETS).map(v=><option key={v}>{v}</option>)}</select></label>
   <Field label="Review date" type="date" value={x.inspection_date} onChange={v=>set("inspection_date",v)}/>
  </div></section>

  <div className="step"><b>02</b><div><h2>Compliance scope</h2><span>Use a project preset or customize the required record set.</span></div></div>
  <section className="card"><div className="presetRow">{Object.keys(PRESETS).map(v=><button key={v} className={x.project_type===v?"preset active": "preset"} onClick={()=>preset(v)}><Building2 size={16}/>{v}</button>)}</div><div className="typeGrid">{TYPES.map(([id,t,d])=><button className={"type "+(x.required.includes(id)?"selected":"")} onClick={()=>toggle("required",id)} key={id}><span className="tick">{x.required.includes(id)?"✓":""}</span><span><b>{t}</b><small>{d}</small></span></button>)}</div></section>

  <div className="step"><b>03</b><div><h2>Evidence intake</h2><span>PDF is not the only option. Add the records you already have.</span></div></div>
  <section className="card"><label className="drop"><UploadCloud size={32}/><b>Drop files here or browse</b><span>PDF · DOCX · XLSX · CSV · TXT · MD · JPG · PNG · WEBP</span><small>For scanned images, OCR requires an installed OCR engine.</small><input type="file" multiple accept=".pdf,.docx,.xlsx,.csv,.txt,.md,.png,.jpg,.jpeg,.webp" onChange={e=>addFiles(Array.from(e.target.files||[]))}/></label>{files.length>0&&<div className="fileList">{files.map((f,i)=><div className="file" key={i}><FileCheck2 size={17}/><div><b>{f.name}</b><span>{Math.round(f.size/1024)} KB</span></div><button type="button" onClick={()=>removeFile(i)}><X size={14}/></button></div>)}</div>}</section>

  <div className="step"><b>04</b><div><h2>Insurance requirements</h2><span>Configure coverage expectations when they are known.</span></div></div>
  <section className="grid2"><section className="card"><label className="field"><span>Minimum liability limit</span><input value={x.minimum} onChange={e=>set("minimum",e.target.value)} placeholder="e.g. 5000000"/></label><label className="field"><span>Renewal alert window (days)</span><input type="number" value={x.renewal} onChange={e=>set("renewal",e.target.value)}/></label></section><section className="card"><label className="field"><span>Required coverage names</span><input value={x.coverages.join(", ")} onChange={e=>set("coverages",e.target.value.split(",").map(s=>s.trim()).filter(Boolean))}/></label><p className="hint">Use names that should appear in the policy, such as General Liability, Professional Indemnity or Workers Compensation.</p></section></section>

  <div className="step"><b>05</b><div><h2>Review context</h2><span>Optional notes and exceptions.</span></div></div>
  <section className="card"><textarea value={x.notes} onChange={e=>set("notes",e.target.value)} placeholder="Project-specific requirements, authority notes, insurance exceptions, contract requirements or reviewer comments..."/></section>

  <section className="actionBar"><div><ShieldCheck size={23}/><div><b>Ready for compliance screening</b><span>{files.length} file(s) · {x.required.length} required record type(s) · {x.coverages.length} coverage expectation(s)</span></div></div><button type="button" className="primary" disabled={busy} onClick={run}>{busy?"Analyzing evidence…":"Run Compliance Inspection"}<ChevronRight size={17}/></button></section>
  {err&&<div className="error"><AlertTriangle size={18}/>{err}</div>}
 </main><footer>Preliminary screening only · Compliance, legal and insurance decisions require qualified human verification.</footer></>
}

function Results({r,onNew,onTab}){
 const pass=r.findings_count===0&&!r.errors?.length;
 return <><Header activeTab="compliance" onTab={onTab} onNew={onNew}/><main>
  <section className="resultHero"><div><p className="eyebrow">SCREENING COMPLETE</p><h1>Compliance Intelligence Report</h1><p>{r.project_name||r.project_id} · {r.project_id} · {r.inspection_id}</p></div><div className={"decision "+(pass?"pass":"risk")}><span>{pass?"PASS":"ATTENTION"}</span><b>{r.compliance_score}/100</b><small>{r.status.replaceAll("_"," ")}</small></div></section>
  <section className="metrics"><Metric icon={<ShieldCheck/>} label="Compliance score" value={r.compliance_score+"/100"}/><Metric icon={<FileCheck2/>} label="Documents received" value={r.documents_received}/><Metric icon={<FileWarning/>} label="Findings" value={r.findings_count}/><Metric icon={<AlertTriangle/>} label="Highest severity" value={r.highest_severity}/></section>
  <section className="reportGrid">
   <section className="card"><Title icon={<FileCheck2/>} text="Document register"/>{r.document_register.length?r.document_register.map((d,i)=><div className="docRow" key={i}><div><b>{d.filename}</b><span>{d.document_type.replaceAll("_"," ")} · {d.extraction_method}</span>{Object.entries(d.fields||{}).filter(([,v])=>v).slice(0,3).map(([k,v])=><small key={k}>{k.replaceAll("_"," ")}: {v}</small>)}</div><span className={"tag "+(d.document_type==="unknown"?"warn":"ok")}>{d.document_type==="unknown"?"REVIEW":"RECOGNIZED"}</span></div>):<Empty text="No documents received."/>}</section>
   <section className="card"><Title icon={<CalendarDays/>} text="Validity & coverage summary"/>{r.document_register.filter(d=>Object.values(d.fields||{}).some(Boolean)).map((d,i)=><div className="summary" key={i}><b>{d.filename}</b>{Object.entries(d.fields||{}).filter(([,v])=>v).map(([k,v])=><div key={k}><span>{k.replaceAll("_"," ")}</span><strong>{v}</strong></div>)}</div>)}{!r.document_register.some(d=>Object.values(d.fields||{}).some(Boolean))&&<Empty text="No structured validity fields were extracted."/>}</section>
  </section>
  <section className="card"><Title icon={<AlertTriangle/>} text="Findings & recommended actions"/>{r.findings.length?r.findings.map((f,i)=><div className="finding" key={i}><div className="findingHead"><div><p className="eyebrow">{f.category}</p><h3>{f.title}</h3></div><span className={"severity "+f.severity.toLowerCase()}>{f.severity}</span></div><p>{f.description}</p><small>Confidence {Math.round(f.confidence*100)}% · {f.document||"Project-level check"}</small><aside><b>Recommended action</b><span>{f.recommended_action}</span></aside></div>):<div className="passBox"><CheckCircle2/><div><b>No actionable findings</b><span>All configured baseline checks passed.</span></div></div>}</section>
  <section className="card"><Title icon={<ShieldCheck/>} text="Next actions"/><ol className="actions">{r.recommendations.map((v,i)=><li key={i}>{v}</li>)}</ol></section>
  {r.errors?.length>0&&<section className="card"><Title icon={<AlertTriangle/>} text="Extraction issues"/>{r.errors.map((e,i)=><div className="warning" key={i}>{e}</div>)}</section>}
 </main><footer>Human verification required for legal, regulatory, insurance and contractual decisions.</footer></>
}
function WorkspaceTab({tab,files,state,register=[],onFilesChange,onFileRemove,onStateChange,onTab}){
 const isRegister=tab==="register";
 const displayedFiles=register.length?register:files;
 return <><section className="hero"><div><p className="eyebrow">CONSTRUCTION INTELLIGENCE HUB</p><h1>{isRegister?"Document Register":"Insurance Workspace"}</h1><p>{isRegister?"Add, remove and review evidence for the compliance inspection.":"Set the coverage limits and renewal rules used by the inspection."}</p></div><div className="statusCard"><ShieldCheck size={25}/><b>{isRegister?displayedFiles.length+" document(s)":"Coverage requirements ready"}</b><span>{isRegister?"Evidence is sent with the next inspection.":"Changes are saved to this review."}</span></div></section><section className="card tabPanel">{isRegister?<><Title icon={<FileCheck2/>} text={register.length?"Inspection document register":"Selected evidence"}/>{register.length?register.map((document,index)=><div className="docRow" key={index}><div><b>{document.filename}</b><span>{document.document_type.replaceAll("_"," ")} · {document.extraction_method}</span>{Object.entries(document.fields||{}).filter(([,value])=>value).slice(0,3).map(([key,value])=><small key={key}>{key.replaceAll("_"," ")}: {value}</small>)}</div><span className={"tag "+(document.document_type==="unknown"?"warn":"ok")}>{document.document_type==="unknown"?"REVIEW":"RECOGNIZED"}</span></div>):files.length?files.map((file,index)=><div className="docRow" key={index}><div><b>{file.name}</b><span>{Math.round(file.size/1024)} KB · {file.type||"file"}</span></div><button type="button" className="fileRemove" onClick={()=>onFileRemove(index)}><X size={14}/><span>Remove</span></button></div>):<Empty text="No documents selected yet."/>}{!register.length&&<label className="drop compactDrop"><UploadCloud size={24}/><b>Add documents</b><span>PDF, DOCX, XLSX, CSV, TXT, JPG or PNG</span><input type="file" multiple accept=".pdf,.docx,.xlsx,.csv,.txt,.md,.png,.jpg,.jpeg,.webp" onChange={event=>onFilesChange(Array.from(event.target.files||[]))}/></label>}</>:<><Title icon={<ShieldCheck/>} text="Insurance requirements"/><div className="fields"><Field label="Minimum liability limit" value={state.minimum} onChange={value=>onStateChange("minimum",value)} placeholder="e.g. 5000000"/><Field label="Renewal alert window (days)" type="number" value={state.renewal} onChange={value=>onStateChange("renewal",value)}/><Field label="Required coverage names" value={state.coverages.join(", ")} onChange={value=>onStateChange("coverages",value.split(",").map(item=>item.trim()).filter(Boolean))} placeholder="General Liability, Workers Compensation"/></div><p className="hint">These saved requirements are included when you run the compliance inspection.</p></>}</section><button type="button" className="primary tabReturn" onClick={()=>onTab("compliance")}>{isRegister?"Continue to Compliance":"Review Compliance"}<ChevronRight size={17}/></button></>;
}
function ReviewTab({tab,r,files,state,onFilesChange,onFileRemove,onStateChange,onTab,onNew}){
 return <><Header activeTab={tab} onTab={onTab} onNew={onNew}/><main><WorkspaceTab tab={tab} files={files} state={state} register={r.document_register} onFilesChange={onFilesChange} onFileRemove={onFileRemove} onStateChange={onStateChange} onTab={onTab}/><section className="card"><Title icon={<FileCheck2/>} text="Latest inspection"/><p className="hint">{r.project_name||r.project_id} · {r.inspection_id}</p></section></main><footer>Human verification required for legal, regulatory, insurance and contractual decisions.</footer></>;
}
function Title({icon,text}){return <div className="title">{icon}<b>{text}</b></div>}
function Metric({icon,label,value}){return <div className="metric"><div>{icon}</div><span>{label}</span><b>{value}</b></div>}
function Field({label,value,onChange,placeholder,type="text"}){return <label className="field"><span>{label}</span><input type={type} value={value} onChange={e=>onChange(e.target.value)} placeholder={placeholder}/></label>}
function Empty({text}){return <div className="empty">{text}</div>}
createRoot(document.getElementById("root")).render(<App/>);
