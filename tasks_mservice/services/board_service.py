import uuid

from api.schemas import (
    BoardCreate,
    BoardPriceInfo,
    BoardUpdate,
    TaskCreate,
    TaskPriceInfo,
)
from db.models import BoardDocument, TaskDocument
from db.repositories import BoardRepository, PageRepository, TaskRepository
from pymongo.asynchronous.database import AsyncDatabase
from utils.check_access import check_if_accessable

from .exceptions import BusinessLogicError, NotFoundError, PermissionDeniedError
from .task_service import TaskService


class BoardService:
    def __init__(
        self,
        task_repo: TaskRepository,
        board_repo: BoardRepository,
        page_repo: PageRepository,
        task_service: TaskService,
        db: AsyncDatabase,
    ):
        self.task_repo = task_repo
        self.board_repo = board_repo
        self.page_repo = page_repo
        self.task_service = task_service
        self.db = db

    async def _ensure_access(self, user_id: int, project_id: str):
        if not await check_if_accessable(user_id, project_id, self.db):
            raise PermissionDeniedError(f"Access denied to project {project_id}")

    async def create_board(
        self, board_data: BoardCreate, page_id: str, user_id: int
    ) -> BoardDocument:
        """(C) Створює нову дошку і прив'язує до сторінки"""
        page = await self.page_repo.get_by_id(page_id)
        if not page:
            raise NotFoundError(f"Page {page_id} not found")

        await self._ensure_access(user_id, page.project_id)

        board_dict = board_data.model_dump()
        board_dict["_id"] = str(uuid.uuid4())
        board_dict["page_id"] = page_id
        board_dict["project_id"] = page.project_id
        board_dict["task_ids"] = []

        new_board = await self.board_repo.create(board_dict)

        await self.page_repo.add_board_id(page_id, new_board.id)

        return new_board

    async def get_board(self, board_id: str, user_id: int) -> BoardDocument:
        """(R) Отримати дошку."""
        board = await self.board_repo.get_by_id(board_id)
        if not board:
            raise NotFoundError(f"Board {board_id} not found")

        await self._ensure_access(user_id, board.project_id)
        return board

    async def delete_board(self, board_id: str, user_id: int) -> dict:
        """(D) Каскадно видаляє дошку і всі її таски"""
        board = await self.get_board(board_id, user_id)
        if not board:
            raise NotFoundError(f"Board {board_id} not found")

        deleted_tasks_count = await self.task_repo.delete_by_board_id(board_id)

        await self.board_repo.delete(board_id)

        await self.page_repo.remove_board_id(board.page_id, board_id)

        return {"deleted_board": board_id, "deleted_tasks": deleted_tasks_count}

    async def update_board(
        self, board_id: str, update_data: BoardUpdate, user_id: int
    ) -> BoardDocument:
        """(U) Оновлює дошку"""
        _ = await self.get_board(board_id, user_id)

        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            raise BusinessLogicError("No fields to update")

        success = await self.board_repo.update(board_id, update_dict)

        if not success:
            raise NotFoundError(f"Board {board_id} not found or no changes made")

        return await self.board_repo.get_by_id(board_id)

    async def create_task_in_board(
        self, task_data: TaskCreate, board_id: str, user_id: int
    ) -> TaskDocument:
        """(C) Створює таск в дошці"""
        board = await self.get_board(board_id, user_id)
        if not board:
            raise NotFoundError(f"Board {board_id} not found")

        task_dict = task_data.model_dump()
        task_dict["_id"] = str(uuid.uuid4())
        task_dict["board_id"] = board.id
        task_dict["project_id"] = board.project_id
        task_dict["time_to_compplete"] = None

        new_task = await self.task_repo.create(task_dict)
        await self.board_repo.add_task_id(board.id, new_task.id)
        return new_task

    async def delete_task(self, task_id: str, user_id: int) -> dict:
        """(D) Видаляє таск і відв'язує його"""
        task = await self.task_service.get_task(task_id, user_id)
        if not task:
            raise NotFoundError(f"Task {task_id} not found")

        await self.task_repo.delete(task_id)
        await self.board_repo.remove_task_id(task.board_id, task.id)

        return {"deleted_task": task.id}

    async def move_task_between_boards(
        self, task_id, giver_board_id, receiver_board_id: str, user_id: str
    ) -> dict:
        """(U) Переміщує таск"""
        task = await self.task_service.get_task(task_id, user_id)
        if not task or task.board_id != giver_board_id:
            raise NotFoundError(f"Task {task_id} not found on board {giver_board_id}")

        receiver_board = await self.get_board(receiver_board_id, user_id)
        if receiver_board.project_id != task.project_id:
            raise BusinessLogicError("Cannot move task between different projects")

        remove_ok = await self.board_repo.remove_task_id(giver_board_id, task_id)
        if not remove_ok:
            raise BusinessLogicError(f"Task {task_id} already moved or not in list")

        add_ok = await self.board_repo.add_task_id(receiver_board_id, task_id)
        if not add_ok:
            # Компенсація: повертаємо таск назад
            await self.board_repo.add_task_id(giver_board_id, task_id)
            raise BusinessLogicError(f"Failed to add task to board {receiver_board_id}")

        update_ok = await self.task_repo.update_board_id(task_id, receiver_board_id)
        if not update_ok:
            # Повна компенсація: переміщуємо ID таска назад
            await self.board_repo.remove_task_id(receiver_board_id, task_id)
            await self.board_repo.add_task_id(giver_board_id, task_id)
            raise BusinessLogicError("Failed to update task's internal board_id")

        return {"status": "success", "task_id": task_id, "new_board": receiver_board_id}

    async def get_board_price_report(self, board_id: str, user_id: int):
        """
        Розраховує фінансовий звіт для ОДНІЄЇ дошки.
        """
        board = await self.get_board(board_id, user_id)
        if not board:
            raise NotFoundError(f"Board {board_id} not found")

        board_total_cost = 0.0
        tasks_reports = []

        tasks = await self.task_repo.get_by_board_id(board.id)

        for task in tasks:
            (task_cost, cost_breakdown) = (
                self.task_service.calculate_task_price_details(task)
            )

            tasks_reports.append(
                TaskPriceInfo(
                    task_id=task.id,
                    name=task.name,
                    total_cost=task_cost if task_cost > 0 else None,
                    cost_breakdown=cost_breakdown,
                )
            )
            board_total_cost += task_cost

        return BoardPriceInfo(
            board_id=board.id,
            name=board.name,
            overall=board_total_cost,
            per_task=tasks_reports,
        )
