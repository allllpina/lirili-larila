from api.dependencies import get_board_service, get_task_service
from api.schemas import TaskCreate, TaskDocument, TaskMoveRequest, TaskUpdate
from fastapi import APIRouter, Depends, HTTPException, Request
from services.board_service import BoardService
from services.exceptions import NotFoundError, PermissionDeniedError
from services.task_service import TaskService
from utils.check_access import get_user_data

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/create_task", response_model=TaskDocument)
async def create_task(
    task: TaskCreate,
    board_id: str,
    request: Request,
    user_data: dict = Depends(get_user_data),
    service: BoardService = Depends(get_board_service),  # <-- BoardService!
):
    try:
        user_id = user_data["user_data"]["id"]
        new_task = await service.create_task_in_board(task, board_id, user_id)

        await request.app.state.SOCKETS.broadcast(
            room=new_task.project_id,
            message={
                "category": "tasks",
                "content": new_task.model_dump(),
                "operation": "create",
            },
        )
        return new_task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/delete_task/{task_id}")
async def delete_task(
    task_id: str,
    request: Request,
    user_data: dict = Depends(get_user_data),
    # Використовуємо BoardService, бо треба видалити ID зі списку дошки
    service: BoardService = Depends(get_board_service),
    # Але нам треба отримати TaskService, щоб дізнатись project_id перед видаленням
    task_service: TaskService = Depends(get_task_service),
):
    try:
        user_id = user_data["user_data"]["id"]

        # Отримуємо таск, щоб знати project_id
        task_doc = await task_service.get_task(task_id, user_id)
        project_id = task_doc.project_id

        # Видаляємо через BoardService
        result = await service.delete_task(task_id, user_id)

        await request.app.state.SOCKETS.broadcast(
            room=project_id,
            message={
                "category": "tasks",
                "content": {"id": task_id},
                "operation": "delete",
            },
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/move_task")
async def move_task(
    move_data: TaskMoveRequest,
    request: Request,
    user_data: dict = Depends(get_user_data),
    service: BoardService = Depends(get_board_service),  # <-- BoardService!
    task_service: TaskService = Depends(get_task_service),
):
    try:
        user_id = user_data["user_data"]["id"]

        # Отримуємо таск для project_id
        task_doc = await task_service.get_task(move_data.taskId, user_id)

        await service.move_task_between_boards(
            task_id=move_data.taskId,
            giver_board_id=move_data.boardGiverId,
            receiver_board_id=move_data.boardReceiverId,
            user_id=user_id,
        )

        await request.app.state.SOCKETS.broadcast(
            room=task_doc.project_id,
            message={
                "category": "tasks",
                # Повертаємо дані про переміщення, щоб фронт оновив UI
                "content": move_data.model_dump(),
                "operation": "move",
            },
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- ОПЕРАЦІЇ ЧЕРЕЗ TASK SERVICE (Зміна контенту) ---


@router.get("/get_task/{task_id}", response_model=TaskDocument)
async def get_task(
    task_id: str,
    user_data: dict = Depends(get_user_data),
    service: TaskService = Depends(get_task_service),  # <-- TaskService!
):
    try:
        user_id = user_data["user_data"]["id"]
        task = await service.get_task(task_id, user_id)

        (price, details) = service.calculate_task_price_details(task)

        response = task.model_dump()
        response["price"] = price
        # Можна додати details в response, якщо модель TaskResponse це підтримує
        return response
    except (NotFoundError, PermissionDeniedError) as e:
        raise HTTPException(
            status_code=404 if isinstance(e, NotFoundError) else 403, detail=str(e)
        )


@router.put("/edit_task", response_model=TaskDocument)
async def edit_task(
    task_update: TaskUpdate,
    task_id: str,
    request: Request,
    user_data: dict = Depends(get_user_data),
    service: TaskService = Depends(get_task_service),  # <-- TaskService!
):
    try:
        user_id = user_data["user_data"]["id"]
        updated_task = await service.update_task(task_id, task_update, user_id)

        await request.app.state.SOCKETS.broadcast(
            room=updated_task.project_id,
            message={
                "category": "tasks",
                "content": updated_task.model_dump(),
                "operation": "edit",
            },
        )
        return updated_task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
