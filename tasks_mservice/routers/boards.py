from datetime import datetime

from entities_module.entities import Board, Page
from fastapi import APIRouter, Depends, HTTPException, Request
from models.entity_models import BoardEdit, BoardMove, BoardTemplate
from pymongo.database import Database
from utils.check_access import check_if_accessable, get_user_data
from utils.get_db import get_db

boards_router = APIRouter(tags=["boards", "CRUD"])


@boards_router.post("/create_board", tags=["create"])
async def create_board(
    board: BoardTemplate,
    db: Database = Depends(get_db),
    user_data=Depends(get_user_data),
    request: Request = None,
):
    try:
        # Check, if user have an access to CRUD with this project
        is_accessible = await check_if_accessable(
            user_id=user_data["user_data"]["id"],
            project_id=board.project_id,
            db=db,
        )
        if not is_accessible:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource.",
            )

        # Can be changed to JWT
        data = board.model_dump(by_alias=True)

        date_of_creation = str(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        data["date_of_creation"] = date_of_creation

        page_id = data.pop("page_id")
        page = await Page.from_db(id=page_id, db=db)
        try:
            await page.add_boards(boards=[data], write_to_db=True)

            await request.app.state.SOCKETS.broadcast(
                room=board.project_id,
                message={"category": "boards", "content": data, "operation": "create"},
            )

            return data
        except RuntimeError as e:
            raise e
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@boards_router.get("/get_board", tags=["read"])
async def get_board(
    board_id: str,
    project_id,
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

        board = await Board.from_db(board_id, db=db)

        return board.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@boards_router.put("/edit_board", tags=["edit"])
async def edit_board(
    board_template: BoardEdit,
    db: Database = Depends(get_db),
    user_data=Depends(get_user_data),
    request: Request = None,
):
    try:
        # Check, if user have an access to CRUD with this project
        is_accessible = await check_if_accessable(
            user_id=user_data["user_data"]["id"],
            project_id=board_template.project_id,
            db=db,
        )
        if not is_accessible:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource.",
            )

        data = board_template.model_dump(exclude_none=True, by_alias=True)
        board_id = data.pop("_id", None)
        board = await Board.from_db(id=board_id, db=db)

        await board.update(**data)

        await request.app.state.SOCKETS.broadcast(
            room=board.project_id,
            message={"category": "boards", "content": data, "operation": "edit"},
        )

        return board.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@boards_router.delete("/delete_board", tags=["delete"])
async def delete_board(
    board_id: str,
    project_id: str,
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

        board = await Board.from_db(id=board_id, db=db)
        ret = await board.delete_in_db()

        await request.app.state.SOCKETS.broadcast(
            room=board.project_id,
            message={"category": "boards", "content": None, "operation": "delete"},
        )
        return ret
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@boards_router.put("/move_board", tags=["move"])
async def move_board(
    request: BoardMove,
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

        pageGiver = await Page.from_db(id=request.pageGiverId, db=db)
        pageReceiver = await Page.from_db(id=request.pageReceiverId, db=db)

        await pageReceiver.add_boards(boards=[request.boardId], write_to_db=True)
        await pageGiver.delete_board(board_id=request.boardId)

        await req.app.state.SOCKETS.broadcast(
            room=request.project_id,
            message={"category": "boards", "content": request, "operation": "move"},
        )
        return True

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))
