from datetime import datetime

from entities_module.entities import Board, Task
from fastapi import APIRouter, Depends, HTTPException
from models.entity_models import CustomFieldMove, TaskEdit, TaskMove, TaskTemplate
from pymongo.database import Database
from utils.get_db import get_db

tasks_router = APIRouter(tags=["task", "CRUD"])


@tasks_router.post("/create_task", tags=["tasks", "create"])
async def create_task(task: TaskTemplate, db: Database = Depends(get_db)):
    try:
        # Can be changed to JWT
        data = task.model_dump(by_alias=True)

        date_of_creation = str(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        data["date_of_creation"] = date_of_creation

        _ = data.pop("user_id")
        board_id = data.pop("board_id")
        board = await Board.from_db(id=board_id, db=db)
        try:
            await board.add_tasks(tasks=[data], write_to_db=True)

            return data
        except RuntimeError as e:
            raise e
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@tasks_router.get("/get_task", tags=["tasks", "read"])
async def get_task(user_id: int, task_id: str, db: Database = Depends(get_db)):
    try:
        task = await Task.from_db(id=task_id, db=db)

        return task.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@tasks_router.put("/edit_task", tags=["tasks", "edit"])
async def edit_task(task_template: TaskEdit, db: Database = Depends(get_db)):
    try:
        data = task_template.model_dump(exclude_none=True, by_alias=True)
        _ = data.pop("user_id")
        task_id = data.pop("_id")
        task = await Task.from_db(id=task_id, db=db)

        await task.update(**data)

        return task.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@tasks_router.delete("/delete_task", tags=["delete"])
async def delete_task(task_id: str, db: Database = Depends(get_db)):
    # Make it to depend on Project instance
    try:
        task = await Task.from_db(task_id=task_id, db=db)
        ret = await task.delete_in_db()
        return ret
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@tasks_router.put("/move_task", tags=["move"])
async def move_task(request: TaskMove, db: Database = Depends(get_db)):
    try:
        boardGiver = await Board.from_db(id=request.boardGiverId, db=db)
        boardReceiver = await Board.from_db(id=request.boardReceiverId, db=db)

        await boardReceiver.add_tasks(tasks=[request.taskId], write_to_db=True)
        await boardGiver.delete_task(task_id=request.taskId)

        return True

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@tasks_router.put("/move_custom_field", tags=["move"])
async def move_custom_field(request: CustomFieldMove, db: Database = Depends(get_db)):
    try:
        taskGiver = await Task.from_db(id=request.taskGiverId, db=db)
        taskReceiver = await Task.from_db(id=request.taskReceiverId, db=db)

        await taskReceiver.add_custom_field(
            template=request.customField, write_to_db=True
        )
        await taskGiver.delete_custom_field(custom_field=request.customField)

        return True

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))
