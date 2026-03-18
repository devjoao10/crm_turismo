from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.dependencies.auth import get_current_user
from app.db.database import get_db
from app.models.lead import Lead
from app.models.user import User
from app.models.pipeline import Pipeline

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, db: Session = Depends(get_db)):

    try:
        user = get_current_user(request)

    except:
        return RedirectResponse(url="/login", status_code=303)

    total_leads = db.query(Lead).count()
    total_users = db.query(User).count()
    total_pipelines = db.query(Pipeline).count()
    
    # Leads by status
    status_counts = db.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
    leads_by_status = {status: count for status, count in status_counts}

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "total_leads": total_leads,
            "total_users": total_users,
            "total_pipelines": total_pipelines,
            "leads_by_status": leads_by_status
        }
    )