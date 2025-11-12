import uuid

from db.models import ProjectDocument
from db.repositories import ProjectRepository
from models.entity_schemas import (
    FullBoard,
    FullPage,
    FullProject,
    ProjectCreate,
    ProjectPriceReport,
    ProjectUpdate,
)

from .exceptions import BusinessLogicError, NotFoundError
from .page_service import PageService
from .task_service import TaskService


class ProjectService:
    def __init__(
        self,
        project_repo: ProjectRepository,
        page_service: PageService,  # Ін'єктуємо PageService
        task_service: TaskService,  # Ін'єктуємо TaskService
    ):
        self.project_repo = project_repo
        self.page_service = page_service
        self.task_service = task_service

        # Для звітів нам все ще потрібні "сирі" репозиторії
        # Це місце можна оптимізувати, але для початку так
        self.page_repo = page_service.page_repo
        self.board_repo = page_service.board_service.board_repo
        self.task_repo = page_service.board_service.task_service.task_repo

    async def create_project(self, project_data: ProjectCreate) -> ProjectDocument:
        """(C) Створює проект (вже було)"""
        doc_data = project_data.model_dump()
        doc_data["_id"] = str(uuid.uuid4())
        doc_data["page_ids"] = []
        return await self.project_repo.create(doc_data)

    async def update_project(
        self, project_id: str, update_data: ProjectUpdate
    ) -> ProjectDocument:
        """(U) Оновлює проект"""
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            raise BusinessLogicError("No fields to update")

        success = await self.project_repo.update(project_id, update_dict)
        if not success:
            raise NotFoundError(f"Project {project_id} not found or no changes made")

        return await self.project_repo.get_by_id(project_id)

    async def delete_project(self, project_id: str) -> dict:
        """(D) Каскадно видаляє проект -> сторінки -> дошки -> таски"""
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")

        deleted_pages = 0
        deleted_boards = 0
        deleted_tasks = 0

        # 1. Ієрархічно викликаємо PageService
        for page_id in project.page_ids:
            try:
                report = await self.page_service.delete_page(page_id)
                deleted_pages += 1
                deleted_boards += report.get("deleted_boards", 0)
                deleted_tasks += report.get("deleted_tasks", 0)
            except NotFoundError:
                pass

        # 2. Видаляємо сам проект
        await self.project_repo.delete(project_id)

        return {
            "deleted_project": project_id,
            "deleted_pages": deleted_pages,
            "deleted_boards": deleted_boards,
            "deleted_tasks": deleted_tasks,
        }

    async def get_full_project_for_llm(self, project_id: str) -> FullProject:
        """
        Збирає (гідратує) повний JSON проекту для LLM.
        """

        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")

        full_pages = []
        pages = await self.page_repo.get_by_project_id(project.id)

        for page in pages:
            full_boards = []
            boards = await self.board_repo.get_by_page_id(page.id)
            for board in boards:
                tasks = await self.task_repo.get_by_board_id(board.id)
                full_boards.append(FullBoard(**board.model_dump(), tasks=tasks))
            full_pages.append(FullPage(**page.model_dump(), boards=full_boards))

        return FullProject(**project.model_dump(), pages=full_pages)

    async def get_project_price_report(self, project_id: str) -> ProjectPriceReport:
        """
        Розраховує фінансовий звіт для проекту,
        делегуючи роботу сервісу сторінок.
        """
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")

        project_total_cost = 0.0
        pages_reports = []

        for page_id in project.page_ids:
            try:
                page_report = await self.page_service.get_page_price_report(page_id)
                pages_reports.append(page_report)
                project_total_cost += page_report.overall

            except NotFoundError:
                pass

        return ProjectPriceReport(
            project_id=project.id,
            project_name=project.name,
            overall=project_total_cost,
            per_page=pages_reports,
        )
