from config import get_settings
from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse
from models.entity_models import ProjectEdit
from routers.boards import boards_router
from routers.pages import pages_router
from routers.projects import projects_router
from routers.tasks import tasks_router
from utils.check_access import check_if_accessable, get_user_data
from utils.get_db import get_db
from utils.websocket_hub import WSHub

app = FastAPI(title="Tasks service", version="1.0.0", root_path="/lirililarila")

settings = get_settings()
app.state.SOCKETS = WSHub()

app.include_router(prefix="/projects", router=projects_router)
app.include_router(prefix="/pages", router=pages_router)
app.include_router(prefix="/boards", router=boards_router)
app.include_router(prefix="/tasks", router=tasks_router)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(f"{settings.html_path}greetings.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.post("/test")
async def test(
    request: ProjectEdit, user_data=Depends(get_user_data), db=Depends(get_db)
):
    """
    Test endpoint to show, how exactly user separation works
    """
    res = await check_if_accessable(
        user_id=user_data["user_data"]["id"], project_id=request.id, db=db
    )
    return res


# import asyncio

# from entities_module.entities import Project
# from pymongo import AsyncMongoClient


# async def main():
#     client = AsyncMongoClient("localhost", 27017)
#     db = client.get_database("test")

#     project = await Project.from_db("7f5ecfbc-6719-425d-8be9-62cbb3aeac7c", db=db)
#     await project.add_pages(
#         pages=[
#             {
#                 "project_id": "1344a344-ebd4-4a30-a723-7759cb042e07",
#                 "date_of_creation": "31-08-2025 18:40:56",
#                 "name": "test1",
#                 "description": "asdfasdfasdf",
#                 "boards": [],
#             }
#         ]
#     )
#     print(project.dump_to_dict())
# await project.write_to_db()
# # await project.delete_page("1d8e6507-d374-4ef0-a1b4-51c9ca0b4bea", delete_in_db=True)
# await project.update(**{"name": "abobik", "description": "last"})


# asyncio.run(main())
