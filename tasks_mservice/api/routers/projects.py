from typing import List

from api.dependencies import get_project_service, get_task_service, get_users_repo
from api.schemas import (
    FullProject,
    ProjectCreate,
    ProjectDocument,
    ProjectPriceReport,
    ProjectUpdate,
    TaskUpdate,
)
from db.repositories import UsersRepository
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from services.exceptions import NotFoundError, PermissionDeniedError
from services.project_service import ProjectService
from services.task_service import TaskService
from utils.ai_processing import ExpectedResponse as AIResponse
from utils.ai_processing import GoogleAIProcessor as AI
from utils.check_access import decode_jwt_token, get_user_data

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/create_project", response_model=ProjectDocument)
async def create_project(
    project: ProjectCreate,
    user_data: dict = Depends(get_user_data),
    service: ProjectService = Depends(get_project_service),
):
    user_id = user_data["user_data"]["id"]
    return await service.create_project(project, user_id)


@router.get("/get_project/{project_id}", response_model=ProjectDocument)
async def get_project(
    project_id: str,
    user_data: dict = Depends(get_user_data),
    service: ProjectService = Depends(get_project_service),
):
    try:
        user_id = user_data["user_data"]["id"]
        return await service.get_project(project_id, user_id)
    except (NotFoundError, PermissionDeniedError) as e:
        raise HTTPException(
            status_code=404 if isinstance(e, NotFoundError) else 403, detail=str(e)
        )


@router.get("/my_projects", response_model=List[ProjectDocument])
async def get_my_projects(
    user_data: dict = Depends(get_user_data),
    service: ProjectService = Depends(get_project_service),
):
    """
    Отримує список проектів, де користувач є власником або учасником.
    """
    try:
        user_id = user_data["user_data"]["id"]
        return await service.get_user_projects(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/edit_project", response_model=ProjectDocument)
async def edit_project(
    project: ProjectUpdate,
    project_id: str,
    user_data: dict = Depends(get_user_data),
    service: ProjectService = Depends(get_project_service),
):
    try:
        user_id = user_data["user_data"]["id"]
        return await service.update_project(project_id, project, user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/delete_project/{project_id}")
async def delete_project(
    project_id: str,
    user_data: dict = Depends(get_user_data),
    service: ProjectService = Depends(get_project_service),
):
    try:
        user_id = user_data["user_data"]["id"]
        return await service.delete_project(project_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get_cost_evaluation/{project_id}", response_model=ProjectPriceReport)
async def get_cost_evaluation(
    project_id: str,
    user_data: dict = Depends(get_user_data),
    service: ProjectService = Depends(get_project_service),
):
    try:
        user_id = user_data["user_data"]["id"]
        return await service.get_project_price_report(project_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get_ai_evaluation/{project_id}", response_model=AIResponse)
async def get_ai_evaluation(
    project_id: str,
    user_data: dict = Depends(get_user_data),
    service: ProjectService = Depends(get_project_service),
    task_service: TaskService = Depends(get_task_service),
):
    try:
        user_id = user_data["user_data"]["id"]
        full_project: FullProject = await service.get_full_project_for_llm(
            project_id, user_id
        )
        ai_result = await AI.get_priority_and_recomendations(full_project)

        if ai_result.prioritized_tasks:

            for item in ai_result.prioritized_tasks:
                try:
                    update_data = TaskUpdate(priority=item.priority)

                    await task_service.update_task(
                        task_id=item.task_id, update_data=update_data, user_id=user_id
                    )
                except Exception:
                    # Якщо один таск не оновився (наприклад, видалений), не ламаємо весь запит
                    continue

        return ai_result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.websocket("/ws/{project_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    project_id: str,
    users_repo: UsersRepository = Depends(get_users_repo),
):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008, reason="Missing Token")
        return

    try:
        payload = decode_jwt_token(token)
        user_id = payload.get("user_data", {}).get("id")
    except ValueError:
        await websocket.close(code=1008, reason="Invalid Token")
        return

    is_accessible = await users_repo.check_access(user_id, project_id)
    if not is_accessible:
        await websocket.close(code=1008, reason="Access Denied")
        return

    await websocket.app.state.SOCKETS.connect_to_room(project_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket.app.state.SOCKETS.disconnect_from_room(project_id, websocket)
