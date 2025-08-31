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

# from entities_module.entities import Board
# from pymongo import AsyncMongoClient


# async def main():
#     client = AsyncMongoClient("localhost", 27017)
#     db = client.get_database("test")
#     board = await Board.from_db(
#         id="204626b9-345b-4697-9b02-a5511f77cf52",
#         db=db,
#     )
#     await board.add_tasks(
#         [
#             {
#                 "project_id": "897eeefc-f79d-46cd-b268-91eeb9ec2cb6",
#                 "name": "Task-1",
#                 "description": "somedesc1",
#                 "collaborators": [{"usr_id": 1, "role": "admin", "salary": 0}],
#                 "price": -1,
#                 "priority": "low",
#                 "status": "done",
#                 "tags": ["tag1", "tag3"],
#                 "time_to_complete": -1,
#                 "date_of_creation": "30-08-2025 20:01:56",
#                 "custom_fields": [
#                     {"type": "checkbox", "checked": True, "text": "Boba"}
#                 ],
#             },
#             {
#                 "project_id": "897eeefc-f79d-46cd-b268-91eeb9ec2cb6",
#                 "name": "Task-2",
#                 "description": "somedesc2",
#                 "collaborators": [{"usr_id": 1, "role": "admin", "salary": 0}],
#                 "price": -1,
#                 "priority": "high",
#                 "status": "done",
#                 "tags": ["tag1", "tag2", "tag3"],
#                 "time_to_complete": -1,
#                 "date_of_creation": "30-08-2025 20:01:56",
#                 "custom_fields": [],
#             },
#         ],
#         write_to_db=True,
#     )
#     print(board.dump_to_dict())


# asyncio.run(main())
