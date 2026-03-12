from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

TEST_EMAIL = "admin@crm.com"
TEST_PASSWORD = "123456"


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
def login_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    if email == TEST_EMAIL and password == TEST_PASSWORD:
        request.session["user"] = email
        return RedirectResponse(url="/dashboard", status_code=303)

    return templates.TemplateResponse(
        "login.html",
        {   
            "request": request,
            "error": "Email ou senha inválidos."
        }
    )

@router.post("/logout", response_class=HTMLResponse)
def logout(request: Request):
        request.session.clear()
        return RedirectResponse(url="/login", status_code=303)