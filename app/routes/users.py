from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.utils.security import hash_password
from app.dependencies.auth import get_current_user

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/users", response_class=HTMLResponse)
def list_users(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        current_user = get_current_user(request)
    except:
        return RedirectResponse(url="/login", status_code=303)

    users = db.query(User).all()

    return templates.TemplateResponse(
        "users/list.html",
        {
            "request": request,
            "users": users,
            "current_user": current_user
        }
    )


@router.get("/users/create", response_class=HTMLResponse)
def create_user_page(
    request: Request
):
    try:
        current_user = get_current_user(request)
    except:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        "users/create.html",
        {
            "request": request,
            "current_user": current_user,
            "error": None
        }
    )


@router.post("/users/create", response_class=HTMLResponse)
def create_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        current_user = get_current_user(request)
    except:
        return RedirectResponse(url="/login", status_code=303)

    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        return templates.TemplateResponse(
            "users/create.html",
            {
                "request": request,
                "current_user": current_user,
                "error": "Já existe um usuário com esse email."
            }
        )

    new_user = User(
        name=name,
        email=email,
        password=hash_password(password),
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return RedirectResponse(url="/users", status_code=303)