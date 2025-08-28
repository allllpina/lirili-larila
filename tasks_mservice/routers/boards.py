from entities_module.entities import Board
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
        _ = data.pop("user_id")

        board = await Board.from_template(template=data, db=db)
        try:
            await board.write_to_db()

            return board.dump_to_dict()
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
