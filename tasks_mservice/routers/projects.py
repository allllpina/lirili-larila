from datetime import datetime

from entities_module.entities import Project
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from models.entity_models import ProjectEdit, ProjectTemplate
from pymongo.asynchronous.database import AsyncDatabase
from utils.check_access import get_user_data
from utils.get_db import get_db

projects_router = APIRouter(tags=["projects", "CRUD"])


@projects_router.post("/create_project", tags=["projects", "create"])
async def create_project(project: ProjectTemplate, db: AsyncDatabase = Depends(get_db)):
    try:
        # Can be changed to JWT
        data = project.model_dump(by_alias=True)

        date_of_creation = str(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        data["date_of_creation"] = date_of_creation

        project: Project = await Project.from_template(template=data, db=db)

        # to change when JWT is complete
        user_id = data.pop("user_id")
        try:
            collection = db.get_collection("users")
            data_to_write = {
                "_id": project.id,
                "name": project.name,
                "users": [user_id]
                + [collaborator["usr_id"] for collaborator in project.collaborators],
            }

            await collection.insert_one(data_to_write)

        except HTTPException as e:
            raise HTTPException(status_code=500, detail=str(e))

        try:
            await project.write_to_db()
            return project.dump_to_dict()
        except RuntimeError as e:
            raise e
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@projects_router.get("/get_projects", tags=["projects", "read"])
async def get_projects(
    user=Depends(get_user_data),
    db: AsyncDatabase = Depends(get_db),
    collection="users",
):
    try:
        collection = db.get_collection(collection)
        cursor = collection.find(
            {"users": user["user_data"]["id"]},
            {"_id": 1, "name": 1},
        )
        projects = [{"id": doc["_id"], "name": doc["name"]} async for doc in cursor]

        return projects

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@projects_router.get("/get_project", tags=["projects", "read"])
async def get_project(
    user_id: int, project_id: str, db: AsyncDatabase = Depends(get_db)
):
    try:
        project = await Project.from_db(project_id, db=db)

        return project.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@projects_router.put("/edit_project", tags=["projects", "edit"])
async def edit_project(
    project_template: ProjectEdit, db: AsyncDatabase = Depends(get_db)
):
    try:
        data = project_template.model_dump(exclude_none=True, by_alias=True)
        _ = data.pop("user_id", None)
        project_id = data.pop("_id", None)
        project = await Project.from_db(id=project_id, db=db)

        await project.update(**data)

        return project.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@projects_router.delete("/delete_project", tags=["projects", "delete"])
async def delete_project(project_id: str, db: AsyncDatabase = Depends(get_db)):
    try:
        project = await Project.from_db(id=project_id, db=db)
        ret = await project.delete_in_db()
        return ret
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@projects_router.get("/get_cost_evaluation/{project_id}")
async def get_cost_evaluation(project_id: str, db: AsyncDatabase = Depends(get_db)):
    try:
        project = await Project.from_db(project_id, db=db)

        return project.calculate_project_cost()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@projects_router.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """
    Endpoint for websocket connection
    """
    await websocket.app.state.SOCKETS.connect_to_room(
        room=project_id, websocket=websocket
    )

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket.app.state.SOCKETS.disconnect_from_room(
            room=project_id, websocket=websocket
        )
