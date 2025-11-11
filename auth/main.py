from config import get_settings
from fastapi import FastAPI
from routers.auth_router import auth_router
from routers.user_router import user_router
from starlette.middleware.sessions import SessionMiddleware

settings = get_settings()

app = FastAPI(title="Auth service", version="1.0.0", root_path="/auth")
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_middleware_secret.get_secret_value(),
)

app.include_router(auth_router)
app.include_router(user_router)
