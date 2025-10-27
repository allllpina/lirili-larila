from datetime import datetime

from entities_module.entities import Board, Task
from fastapi import APIRouter, Depends, HTTPException, Request
from models.entity_models import CustomFieldMove, TaskEdit, TaskMove, TaskTemplate
from pymongo.database import Database
from utils.check_access import check_if_accessable, get_user_data
from utils.get_db import get_db

tasks_router = APIRouter(tags=["task", "CRUD"])


@tasks_router.post("/create_task", tags=["tasks", "create"])
async def create_task(
    task: TaskTemplate,
    db: Database = Depends(get_db),
    user_data=Depends(get_user_data),
    request: Request = None,
):
    try:
        # Check, if user have an access to CRUD with this project
        is_accessible = await check_if_accessable(
            user_id=user_data["user_data"]["id"],
            project_id=task.project_id,
            db=db,
        )
        if not is_accessible:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource.",
            )
        # Can be changed to JWT
        data = task.model_dump(by_alias=True)

        date_of_creation = str(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        data["date_of_creation"] = date_of_creation

        board_id = data.pop("board_id")
        board = await Board.from_db(id=board_id, db=db)
        try:
            await board.add_tasks(tasks=[data], write_to_db=True)

            await request.app.state.SOCKETS.broadcast(
                room=task.project_id,
                message={"category": "tasks", "content": data, "operation": "create"},
            )
            return data
        except RuntimeError as e:
            raise e
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@tasks_router.get("/get_task", tags=["tasks", "read"])
async def get_task(
    task_id: str,
    project_id: str,
    db: Database = Depends(get_db),
    user_data=Depends(get_user_data),
):
    try:
        # Check, if user have an access to CRUD with this project
        is_accessible = await check_if_accessable(
            user_id=user_data["user_data"]["id"],
            project_id=project_id,
            db=db,
        )
        if not is_accessible:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource.",
            )

        task = await Task.from_db(id=task_id, db=db)

        return task.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@tasks_router.put("/edit_task", tags=["tasks", "edit"])
async def edit_task(
    task_template: TaskEdit,
    db: Database = Depends(get_db),
    user_data=Depends(get_user_data),
    request: Request = None,
):
    try:
        # Check, if user have an access to CRUD with this project
        is_accessible = await check_if_accessable(
            user_id=user_data["user_data"]["id"],
            project_id=task_template.project_id,
            db=db,
        )
        if not is_accessible:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource.",
            )

        data = task_template.model_dump(exclude_none=True, by_alias=True)
        task_id = data.pop("_id")
        task = await Task.from_db(id=task_id, db=db)

        await task.update(**data)

        await request.app.state.SOCKETS.broadcast(
            room=task.project_id,
            message={"category": "tasks", "content": data, "operation": "edit"},
        )

        return task.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@tasks_router.delete("/delete_task", tags=["delete"])
async def delete_task(
    task_id: str,
    project_id,
    db: Database = Depends(get_db),
    user_data=Depends(get_user_data),
    request: Request = None,
):
    # Make it to depend on Project instance
    try:
        # Check, if user have an access to CRUD with this project
        is_accessible = await check_if_accessable(
            user_id=user_data["user_data"]["id"],
            project_id=project_id,
            db=db,
        )
        if not is_accessible:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource.",
            )

        task = await Task.from_db(task_id=task_id, db=db)
        ret = await task.delete_in_db()

        await request.app.state.SOCKETS.broadcast(
            room=task.project_id,
            message={"category": "tasks", "content": None, "operation": "delete"},
        )
        return ret
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@tasks_router.put("/move_task", tags=["move"])
async def move_task(
    request: TaskMove,
    db: Database = Depends(get_db),
    user_data=Depends(get_user_data),
    req: Request = None,
):
    try:
        # Check, if user have an access to CRUD with this project
        is_accessible = await check_if_accessable(
            user_id=user_data["user_data"]["id"],
            project_id=request.project_id,
            db=db,
        )
        if not is_accessible:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource.",
            )

        boardGiver = await Board.from_db(id=request.boardGiverId, db=db)
        boardReceiver = await Board.from_db(id=request.boardReceiverId, db=db)

        await boardReceiver.add_tasks(tasks=[request.taskId], write_to_db=True)
        await boardGiver.delete_task(task_id=request.taskId)

        await req.app.state.SOCKETS.broadcast(
            room=request.project_id,
            message={"category": "tasks", "content": request, "operation": "create"},
        )

        return True

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@tasks_router.put("/move_custom_field", tags=["move"])
async def move_custom_field(
    request: CustomFieldMove,
    db: Database = Depends(get_db),
    user_data=Depends(get_user_data),
    req: Request = None,
):
    try:
        # Check, if user have an access to CRUD with this project
        is_accessible = await check_if_accessable(
            user_id=user_data["user_data"]["id"],
            project_id=request.project_id,
            db=db,
        )
        if not is_accessible:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource.",
            )

        taskGiver = await Task.from_db(id=request.taskGiverId, db=db)
        taskReceiver = await Task.from_db(id=request.taskReceiverId, db=db)

        await taskReceiver.add_custom_field(
            template=request.customField, write_to_db=True
        )
        await taskGiver.delete_custom_field(custom_field=request.customField)

        await request.app.state.SOCKETS.broadcast(
            room=request.project_id,
            message={"category": "tasks", "content": request, "operation": "create"},
        )

        return True

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))
