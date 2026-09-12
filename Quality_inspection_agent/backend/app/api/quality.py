import json
from pathlib import Path
from typing import Annotated
from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from ..quality_agent.agent import QualityInspectionAgent
from ..services.model_config import MODEL_CONFIG
from ..services.file_store import save_upload

router=APIRouter(tags=["Quality Inspection"])
agent=QualityInspectionAgent(MODEL_CONFIG)

@router.get("/capabilities")
def capabilities():
    return agent.capabilities()

@router.post("/inspect")
async def inspect(
    project_id: Annotated[str,Form(...)],
    site_id: Annotated[str|None,Form()]=None,
    zone: Annotated[str|None,Form()]=None,
    area: Annotated[str|None,Form()]=None,
    inspection_mode: Annotated[str,Form()]="comprehensive",
    inspection_categories: Annotated[str,Form()]="crack,concrete,surface,component,corrosion",
    description: Annotated[str|None,Form()]=None,
    measurements: Annotated[str,Form()] = "{}",
    images: Annotated[list[UploadFile],File()] = []
):
    try:
        m=json.loads(measurements or "{}")
        if not isinstance(m,dict): raise ValueError
    except Exception:
        raise HTTPException(status_code=400,detail="Measurements must be a JSON object.")

    names=[]; paths=[]
    for upload in images:
        path,name=await save_upload(upload)
        paths.append(str(path)); names.append(name)

    categories=[x.strip().lower() for x in inspection_categories.split(",") if x.strip()]
    result=agent.inspect({
        "project_id":project_id,"site_id":site_id,"zone":zone,"area":area,
        "inspection_mode":inspection_mode,"inspection_categories":categories,
        "description":description,"measurements":m,"images":paths
    })
    result["images"]=[f"/uploads/{n}" for n in names]
    for f in result["findings"]:
        if f.get("image_id"):
            f["image_id"]=f"/uploads/{Path(f['image_id']).name}"
    return result
