from datetime import datetime

from entities_module.entities import Board, Page
from fastapi import APIRouter, Depends, HTTPException
from models.entity_models import BoardEdit, BoardTemplate
from pymongo.database import Database
from utils.get_db import get_db

boards_router = APIRouter(tags=["boards", "CRUD"])


@boards_router.post("/create_board", tags=["boards", "create"])
async def create_board(board: BoardTemplate, db: Database = Depends(get_db)):
    try:
        # Can be changed to JWT
        data = board.model_dump(by_alias=True)

        date_of_creation = str(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        data["date_of_creation"] = date_of_creation

        _ = data.pop("user_id")
        page_id = data.pop("page_id")
        page = await Page.from_db(id=page_id, db=db)
        try:
            await page.add_boards(boards=[data], write_to_db=True)

            return data
        except RuntimeError as e:
            raise e
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@boards_router.get("/get_board", tags=["boards", "read"])
async def get_board(user_id: int, board_id: str, db: Database = Depends(get_db)):
    try:
        board = await Board.from_db(board_id, db=db)

        return board.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@boards_router.put("/edit_board", tags=["boards", "edit"])
async def edit_board(board_template: BoardEdit, db: Database = Depends(get_db)):
    try:
        data = board_template.model_dump(exclude_none=True, by_alias=True)
        _ = data.pop("user_id", None)
        board_id = data.pop("_id", None)
        board = await Board.from_db(id=board_id, db=db)

        await board.update(**data)

        return board.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@boards_router.delete("/delete_board", tags=["boards", "delete"])
async def delete_board(board_id: str, db: Database = Depends(get_db)):
    # Make it to depend on Project instance
    try:
        board = await Board.from_db(id=board_id, db=db)
        ret = await board.delete_in_db()
        return ret
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))
