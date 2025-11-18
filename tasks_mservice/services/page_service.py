import uuid

from api.schemas import PageCreate, PagePriceInfo, PageUpdate
from db.models import PageDocument
from db.repositories import PageRepository, ProjectRepository
from pymongo.asynchronous.database import AsyncDatabase
from utils.check_access import check_if_accessable

from .board_service import BoardService  # Використовуємо BoardService для каскаду
from .exceptions import BusinessLogicError, NotFoundError, PermissionDeniedError


class PageService:
    def __init__(
        self,
        page_repo: PageRepository,
        project_repo: ProjectRepository,
        board_service: BoardService,  # Потрібен для каскадного видалення
        db: AsyncDatabase,
    ):
        self.page_repo = page_repo
        self.project_repo = project_repo
        self.board_service = board_service  # Сервіс викликає інший сервіс
        self.db = db

    async def _ensure_access(self, user_id: int, project_id: str):
        if not await check_if_accessable(user_id, project_id, self.db):
            raise PermissionDeniedError(f"Access denied to project {project_id}")

    async def create_page(
        self, page_data: PageCreate, project_id: str, user_id: int
    ) -> PageDocument:
        """(C) Створює нову сторінку і прив'язує до проекту"""
        await self._ensure_access(user_id, project_id)

        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")

        page_dict = page_data.model_dump()
        page_dict["_id"] = str(uuid.uuid4())
        page_dict["project_id"] = project_id
        page_dict["board_ids"] = []

        new_page = await self.page_repo.create(page_dict)
        await self.project_repo.add_page_id(project_id, new_page.id)

        return new_page

    async def get_page(self, page_id: str, user_id: int) -> PageDocument:
        """(R) Отримати сторінку."""
        page = await self.page_repo.get_by_id(page_id)
        if not page:
            raise NotFoundError(f"Page {page_id} not found")

        await self._ensure_access(user_id, page.project_id)
        return page

    async def delete_page(self, page_id: str, user_id: int) -> dict:
        """(D) Каскадно видаляє сторінку -> дошки -> таски"""
        page = await self.get_page(page_id, user_id)
        if not page:
            raise NotFoundError(f"Page {page_id} not found")

        deleted_boards_count = 0
        deleted_tasks_count = 0

        # 1. Ієрархічно викликаємо BoardService для кожної дошки
        for board_id in page.board_ids:
            try:
                # BoardService сам видалить дошку і всі її таски
                report = await self.board_service.delete_board(board_id, user_id)
                deleted_boards_count += 1
                deleted_tasks_count += report.get("deleted_tasks", 0)
            except NotFoundError:
                # Дошка вже видалена, нічого страшного
                pass

        # 2. Видаляємо саму сторінку
        await self.page_repo.delete(page_id)

        # 3. Відв'язуємо ID сторінки від проекту
        await self.project_repo.remove_page_id(page.project_id, page_id)

        return {
            "deleted_page": page_id,
            "deleted_boards": deleted_boards_count,
            "deleted_tasks": deleted_tasks_count,
        }

    async def update_page(
        self, page_id: str, update_data: PageUpdate, user_id: int
    ) -> PageDocument:
        """(U) Оновлює сторінку"""
        _ = await self.get_page(page_id, user_id)

        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            raise BusinessLogicError("No fields to update")

        success = await self.page_repo.update(page_id, update_dict)
        if not success:
            raise NotFoundError(f"Page {page_id} not found or no changes made")

        return await self.page_repo.get_by_id(page_id)

    async def get_page_price_report(self, page_id: str, user_id: int) -> PagePriceInfo:
        """
        Розраховує фінансовий звіт для ОДНІЄЇ сторінки.
        """
        page = await self.get_page(page_id, user_id)
        if not page:
            raise NotFoundError(f"Page {page_id} not found")

        page_total_cost = 0.0
        boards_reports = []

        for board_id in page.board_ids:
            try:
                # Викликаємо BoardService, щоб отримати готовий звіт
                board_report = await self.board_service.get_board_price_report(
                    board_id, user_id
                )
                boards_reports.append(board_report)
                page_total_cost += board_report.overall
            except NotFoundError:
                # Дошка не знайдена, пропускаємо
                pass

        return PagePriceInfo(
            page_id=page.id,
            name=page.name,
            overall=page_total_cost,
            per_board=boards_reports,
        )
