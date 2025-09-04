from config import HTML_PATH
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from routers.boards import boards_router
from routers.pages import pages_router
from routers.projects import projects_router
from routers.tasks import tasks_router

app = FastAPI()

app.include_router(prefix="/projects", router=projects_router)
app.include_router(prefix="/pages", router=pages_router)
app.include_router(prefix="/boards", router=boards_router)
app.include_router(prefix="/tasks", router=tasks_router)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(f"{HTML_PATH}greetings.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


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
