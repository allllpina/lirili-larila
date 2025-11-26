from contextlib import asynccontextmanager

from api.routers import boards, pages, projects, tasks
from config import get_settings
from db.database import close_mongo_connection, connect_to_mongo
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.websocket_hub import WSHub


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()

    app.state.SOCKETS = WSHub()
    yield

    await close_mongo_connection()


settings = get_settings()

app = FastAPI(
    title="Tasks Service (Clean Architecture)",
    version="2.0.0",
    lifespan=lifespan,
    root_path="/lirililarila",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],  # Адреса твого фронтенду
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(pages.router)
app.include_router(boards.router)
app.include_router(tasks.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Clean Architecture API"}
