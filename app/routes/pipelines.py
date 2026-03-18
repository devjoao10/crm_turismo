from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import asc
from pydantic import BaseModel

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.pipeline import Pipeline, PipelineStage
from app.models.lead import Lead

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/pipelines", response_class=HTMLResponse)
def list_pipelines(request: Request, db: Session = Depends(get_db)):
    try:
        current_user = get_current_user(request)
    except:
        return RedirectResponse(url="/login", status_code=303)

    pipelines = db.query(Pipeline).all()

    return templates.TemplateResponse(
        "pipelines/list.html",
        {
            "request": request,
            "pipelines": pipelines,
            "current_user": current_user,
            "error": None
        }
    )


@router.post("/pipelines", response_class=HTMLResponse)
def create_pipeline(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    try:
        get_current_user(request)
    except:
        return RedirectResponse(url="/login", status_code=303)

    if not name.strip():
        pipelines = db.query(Pipeline).all()
        return templates.TemplateResponse(
            "pipelines/list.html",
            {
                "request": request,
                "pipelines": pipelines,
                "current_user": get_current_user(request),
                "error": "O nome do funil é obrigatório."
            }
        )

    pipeline = Pipeline(name=name.strip(), description=description.strip())
    db.add(pipeline)
    db.commit()

    return RedirectResponse(url="/pipelines", status_code=303)


@router.post("/pipelines/{pipeline_id}/delete")
def delete_pipeline(pipeline_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        get_current_user(request)
    except:
        return RedirectResponse(url="/login", status_code=303)

    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    if pipeline:
        db.delete(pipeline)
        db.commit()

    return RedirectResponse(url="/pipelines", status_code=303)


@router.get("/pipelines/{pipeline_id}/stages", response_class=HTMLResponse)
def manage_stages(pipeline_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        current_user = get_current_user(request)
    except:
        return RedirectResponse(url="/login", status_code=303)

    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    if not pipeline:
        return RedirectResponse(url="/pipelines", status_code=303)

    stages = db.query(PipelineStage).filter(PipelineStage.pipeline_id == pipeline_id).order_by(PipelineStage.order.asc()).all()

    return templates.TemplateResponse(
        "pipelines/stages.html",
        {
            "request": request,
            "pipeline": pipeline,
            "stages": stages,
            "current_user": current_user,
            "error": None
        }
    )


@router.post("/pipelines/{pipeline_id}/stages", response_class=HTMLResponse)
def create_stage(
    pipeline_id: int,
    request: Request,
    name: str = Form(...),
    order: int = Form(0),
    db: Session = Depends(get_db)
):
    try:
        get_current_user(request)
    except:
        return RedirectResponse(url="/login", status_code=303)

    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    if not pipeline:
        return RedirectResponse(url="/pipelines", status_code=303)

    if not name.strip():
        stages = db.query(PipelineStage).filter(PipelineStage.pipeline_id == pipeline_id).order_by(PipelineStage.order.asc()).all()
        return templates.TemplateResponse(
            "pipelines/stages.html",
            {
                "request": request,
                "pipeline": pipeline,
                "stages": stages,
                "current_user": get_current_user(request),
                "error": "O nome da etapa é obrigatório."
            }
        )

    stage = PipelineStage(pipeline_id=pipeline_id, name=name.strip(), order=order)
    db.add(stage)
    db.commit()

    return RedirectResponse(url=f"/pipelines/{pipeline_id}/stages", status_code=303)


@router.post("/pipelines/stages/{stage_id}/delete")
def delete_stage(stage_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        get_current_user(request)
    except:
        return RedirectResponse(url="/login", status_code=303)

    stage = db.query(PipelineStage).filter(PipelineStage.id == stage_id).first()
    if stage:
        pipeline_id = stage.pipeline_id
        db.delete(stage)
        db.commit()
        return RedirectResponse(url=f"/pipelines/{pipeline_id}/stages", status_code=303)

    return RedirectResponse(url="/pipelines", status_code=303)


@router.get("/pipelines/{pipeline_id}/kanban", response_class=HTMLResponse)
def kanban_board(pipeline_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        current_user = get_current_user(request)
    except:
        return RedirectResponse(url="/login", status_code=303)

    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    if not pipeline:
        return RedirectResponse(url="/pipelines", status_code=303)

    stages = db.query(PipelineStage).filter(PipelineStage.pipeline_id == pipeline_id).order_by(PipelineStage.order.asc()).all()
    
    # Organize leads by stage. For simplicity, leads in a stage are fetched.
    # Leads that don't belong to any stage could be dropped in a generic list if we want,
    # but since this is a specific pipeline kanban, we only show leads in these stages.
    
    stage_ids = [s.id for s in stages]
    leads = db.query(Lead).filter(Lead.pipeline_stage_id.in_(stage_ids)).all()
    
    leads_by_stage = {stage.id: [] for stage in stages}
    for lead in leads:
        leads_by_stage[lead.pipeline_stage_id].append(lead)

    return templates.TemplateResponse(
        "pipelines/kanban.html",
        {
            "request": request,
            "pipeline": pipeline,
            "stages": stages,
            "leads_by_stage": leads_by_stage,
            "current_user": current_user
        }
    )
