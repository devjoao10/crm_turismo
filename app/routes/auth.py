from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
     db: Session = Depends(get_db)
     ):

    user = db.query(User).filter(User.email == email).first()

    if user and user.password == password:
        request.session["user"] = user.email
        return RedirectResponse(url="/dashboard", status_code=303)

    return templates.TemplateResponse(
        "login.html",
        {   
            "request": request,
            "error": "Email ou senha inválidos."
        }
    )

@router.get("/logout", response_class=HTMLResponse)
def logout(request: Request):
        request.session.clear()
        return RedirectResponse(url="/login", status_code=303)