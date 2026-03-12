from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(title="CRM Turismo")

app.add_middleware(SessionMiddleware, secret_key="chave-super-secreta")


app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return RedirectResponse(url="/login")