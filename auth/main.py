from config import get_settings
from fastapi import FastAPI
from routers.auth_router import auth_router
from starlette.middleware.sessions import SessionMiddleware

settings = get_settings()

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_middleware_secret.get_secret_value(),
)

app.include_router(auth_router)
