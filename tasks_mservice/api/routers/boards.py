from api.dependencies import get_board_service
from api.schemas import BoardCreate, BoardDocument, BoardUpdate
from fastapi import APIRouter, Depends, HTTPException, Request
from services.board_service import BoardService
from services.exceptions import NotFoundError, PermissionDeniedError
from utils.check_access import get_user_data

router = APIRouter(prefix="/boards", tags=["Boards"])


@router.post("/create_board", response_model=BoardDocument)
async def create_board(
    board: BoardCreate,
    page_id: str,
    request: Request,
    user_data: dict = Depends(get_user_data),
    service: BoardService = Depends(get_board_service),
):
    try:
        user_id = user_data["user_data"]["id"]
        new_board = await service.create_board(board, page_id, user_id)

        await request.app.state.SOCKETS.broadcast(
            room=new_board.project_id,
            message={
                "category": "boards",
                "content": new_board.model_dump(),
                "operation": "create",
            },
        )
        return new_board
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get_board/{board_id}", response_model=BoardDocument)
async def get_board(
    board_id: str,
    user_data: dict = Depends(get_user_data),
    service: BoardService = Depends(get_board_service),
):
    try:
        user_id = user_data["user_data"]["id"]
        return await service.get_board(board_id, user_id)
    except (NotFoundError, PermissionDeniedError) as e:
        raise HTTPException(
            status_code=404 if isinstance(e, NotFoundError) else 403, detail=str(e)
        )


@router.put("/edit_board", response_model=BoardDocument)
async def edit_board(
    board: BoardUpdate,
    board_id: str,
    request: Request,
    user_data: dict = Depends(get_user_data),
    service: BoardService = Depends(get_board_service),
):
    try:
        user_id = user_data["user_data"]["id"]
        # Оновлюємо
        updated_board = await service.update_board(board_id, board, user_id)

        await request.app.state.SOCKETS.broadcast(
            room=updated_board.project_id,
            message={
                "category": "boards",
                "content": updated_board.model_dump(),
                "operation": "edit",
            },
        )
        return updated_board
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/delete_board/{board_id}")
async def delete_board(
    board_id: str,
    request: Request,
    user_data: dict = Depends(get_user_data),
    service: BoardService = Depends(get_board_service),
):
    try:
        user_id = user_data["user_data"]["id"]

        # 1. Отримуємо дошку, щоб знати project_id для вебсокети
        board_doc = await service.get_board(board_id, user_id)
        project_id = board_doc.project_id

        # 2. Видаляємо
        result = await service.delete_board(board_id, user_id)

        await request.app.state.SOCKETS.broadcast(
            room=project_id,
            message={
                "category": "boards",
                "content": {"id": board_id},
                "operation": "delete",
            },
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
