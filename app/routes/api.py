from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.db.database import get_db
from app.models.lead import Lead
from app.models.pipeline import Pipeline, PipelineStage
from app.models.user import User
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/v1")

# Use a static API KEY for N8N or agent integration
API_KEY = "n8n-integration-secret-key"

def verify_api_access(request: Request, x_api_key: Optional[str] = Header(None)):
    # Check if there is an active session (web user)
    if "user" in request.session:
        return True
    
    # Check if a valid API Key was provided
    if x_api_key == API_KEY:
        return True
    
    raise HTTPException(status_code=403, detail="Acesso não autorizado. Chave de API inválida.")


class LeadStageUpdate(BaseModel):
    pipeline_stage_id: int


@router.put("/leads/{lead_id}/stage", dependencies=[Depends(verify_api_access)])
def update_lead_stage(lead_id: int, payload: LeadStageUpdate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    
    stage = db.query(PipelineStage).filter(PipelineStage.id == payload.pipeline_stage_id).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")
        
    lead.pipeline_stage_id = stage.id
    db.commit()
    
    return {"message": "Lead movido com sucesso"}


# CRUD Endpoints for N8N Integration

class LeadCreate(BaseModel):
    name: str
    email: str
    whatsapp: str
    status: Optional[str] = "novo"
    travel_start_date: str
    travel_end_date: str
    pipeline_stage_id: Optional[int] = None

@router.post("/leads", dependencies=[Depends(verify_api_access)])
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    existing = db.query(Lead).filter(Lead.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Este e-mail de lead já existe.")
        
    try:
        start_date = datetime.strptime(payload.travel_start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(payload.travel_end_date, "%Y-%m-%d").date()
    except:
         raise HTTPException(status_code=400, detail="Datas inválidas. Use YYYY-MM-DD")

    new_lead = Lead(
        name=payload.name,
        email=payload.email,
        whatsapp=payload.whatsapp,
        status=payload.status,
        travel_start_date=start_date,
        travel_end_date=end_date,
        pipeline_stage_id=payload.pipeline_stage_id
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return {"id": new_lead.id, "message": "Lead criado"}

@router.get("/leads", dependencies=[Depends(verify_api_access)])
def get_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    return [{"id": l.id, "name": l.name, "email": l.email, "whatsapp": l.whatsapp, "pipeline_stage_id": l.pipeline_stage_id} for l in leads]

@router.get("/pipelines", dependencies=[Depends(verify_api_access)])
def get_pipelines(db: Session = Depends(get_db)):
    pipelines = db.query(Pipeline).all()
    return [{"id": p.id, "name": p.name} for p in pipelines]

@router.get("/pipelines/{pipeline_id}/stages", dependencies=[Depends(verify_api_access)])
def get_stages(pipeline_id: int, db: Session = Depends(get_db)):
    stages = db.query(PipelineStage).filter(PipelineStage.pipeline_id == pipeline_id).order_by(PipelineStage.order.asc()).all()
    return [{"id": s.id, "name": s.name, "order": s.order} for s in stages]
