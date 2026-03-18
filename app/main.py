from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.routes.users import router as users_router
from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router
from app.routes.leads import router as leads_router
from app.routes.pipelines import router as pipelines_router
from app.routes.api import router as api_router
from app.db.init_db import init_db

app = FastAPI(title="CRM Turismo")

app.add_middleware(SessionMiddleware, secret_key="chave-super-secreta")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(users_router)
app.include_router(leads_router)
app.include_router(pipelines_router)
app.include_router(api_router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return RedirectResponse(url="/login")