from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.utils.security import hash_password
from app.dependencies.auth import get_current_user
from app.services.email_service import send_confirmation_email, confirm_token

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
        is_active=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Enviar email
    send_confirmation_email(request, new_user.email, new_user.name)
    
    return RedirectResponse(url="/users", status_code=303)

@router.post("/users/{user_id}/toggle-active")
def toggle_user_active(user_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        current_user = get_current_user(request)
    except:
        return RedirectResponse(url="/login", status_code=303)
        
    user = db.query(User).filter(User.id == user_id).first()
    
    if user and user.email != current_user.email:
        user.is_active = not user.is_active
        db.commit()
        
    return RedirectResponse(url="/users", status_code=303)

@router.get("/users/confirm/{token}")
def confirm_user_email(token: str, request: Request, db: Session = Depends(get_db)):
    email = confirm_token(token)
    if not email:
        return HTMLResponse("Token inválido ou expirado.", status_code=400)
        
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return HTMLResponse("Usuário não encontrado.", status_code=404)
        
    if user.is_active:
        return RedirectResponse(url="/login", status_code=303)
        
    user.is_active = True
    db.commit()
    return HTMLResponse("Sua conta foi ativada com sucesso! Você já pode fechar esta aba e fazer o login no CRM.")