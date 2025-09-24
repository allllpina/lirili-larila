from fastapi import FastAPI
from routers.auth_router import auth_router
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key="72f7afd228113d3f7d54e0ff5b1dd06e83db74cff9aebea7cd835dfe790ddde7",
)

app.include_router(auth_router)
