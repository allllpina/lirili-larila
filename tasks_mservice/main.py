from contextlib import asynccontextmanager

from api.routers import boards, pages, projects, tasks
from db.database import close_mongo_connection, connect_to_mongo
from fastapi import FastAPI
from utils.websocket_hub import WSHub


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()

    app.state.SOCKETS = WSHub()
    yield

    await close_mongo_connection()


app = FastAPI(
    title="Tasks Service (Clean Architecture)",
    version="2.0.0",
    lifespan=lifespan,
    root_path="/lirililarila",
)

app.include_router(projects.router)
app.include_router(pages.router)
app.include_router(boards.router)
app.include_router(tasks.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Clean Architecture API"}
