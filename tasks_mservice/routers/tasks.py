from entities_module.entities import Task
from fastapi import APIRouter, Depends, HTTPException
from models.entity_models import TaskEdit, TaskTemplate
from pymongo.database import Database
from utils.get_db import get_db

tasks_router = APIRouter(tags=["task", "CRUD"])


@tasks_router.post("/create_task", tags=["task", "create"])
async def create_task(task: TaskTemplate, db: Database = Depends(get_db)):
    try:
        # Can be changed to JWT
        data = task.model_dump(by_alias=True)
        _ = data.pop("user_id")

        task = await Task.from_template(template=data, db=db)
        try:
            await task.write_to_db()

            return task.dump_to_dict()
        except RuntimeError as e:
            raise e
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@tasks_router.get("/get_task", tags=["tasks", "read"])
async def get_task(user_id: int, board_id: str, db: Database = Depends(get_db)):
    try:
        task = await Task.from_db(board_id, db=db)

        return task.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@tasks_router.put("/edit_task", tags=["tasks", "edit"])
async def edit_task(task_template: TaskEdit, db: Database = Depends(get_db)):
    try:
        data = task_template.model_dump(exclude_none=True, by_alias=True)
        _ = data.pop("user_id", None)
        task_id = data.pop("_id", None)
        task = await Task.from_db(id=task_id, db=db)

        await task.update(**data)

        return task.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))
