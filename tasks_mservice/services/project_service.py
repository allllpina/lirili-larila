import uuid
from typing import List

from api.schemas import (
    FullBoard,
    FullPage,
    FullProject,
    ProjectCreate,
    ProjectPriceReport,
    ProjectUpdate,
)
from db.models import ProjectDocument
from db.repositories import (
    BoardRepository,
    PageRepository,
    ProjectRepository,
    TaskRepository,
    UsersRepository,
)
from pymongo.asynchronous.database import AsyncDatabase

from .exceptions import BusinessLogicError, NotFoundError, PermissionDeniedError
from .page_service import PageService


class ProjectService:
    def __init__(
        self,
        project_repo: ProjectRepository,
        page_repo: PageRepository,  # Потрібні для LLM dump
        board_repo: BoardRepository,  # Потрібні для LLM dump
        task_repo: TaskRepository,  # Потрібні для LLM dump
        users_repo: UsersRepository,
        db: AsyncDatabase,
        page_service: PageService,
    ):
        self.project_repo = project_repo
        self.page_repo = page_repo
        self.board_repo = board_repo
        self.task_repo = task_repo
        self.users_repo = users_repo
        self.db = db
        self.page_service = page_service

    async def _ensure_access(self, user_id: int, project_id: str):
        if not await self.users_repo.check_access(project_id, user_id):
            raise PermissionDeniedError(f"Access denied to project {project_id}")

    async def create_project(
        self, project_data: ProjectCreate, user_id: int
    ) -> ProjectDocument:
        """(C) Створює проект"""
        doc_data = project_data.model_dump()
        doc_data["_id"] = str(uuid.uuid4())
        doc_data["page_ids"] = []
        new_project = await self.project_repo.create(doc_data)

        await self.users_repo.set_users(
            new_project.id, new_project.name, user_id, new_project.collaborators
        )

        return new_project

    async def get_project(self, project_id: str, user_id: int) -> ProjectDocument:
        """(R) Отримати проект."""
        # Спочатку перевірка доступу, бо ми не знаємо чи існує проект,
        # але users_repo.check_access перевіряє права по 'users' колекції
        await self._ensure_access(user_id, project_id)

        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")
        return project

    async def get_user_projects(self, user_id: int) -> List[ProjectDocument]:
        """(R) Отримати список усіх проектів користувача."""
        return await self.project_repo.get_projects_by_user(user_id)

    async def update_project(
        self, project_id: str, update_data: ProjectUpdate, user_id: int
    ) -> ProjectDocument:
        """(U) Оновлює проект"""
        await self._ensure_access(user_id, project_id)

        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            raise BusinessLogicError("No fields to update")

        success = await self.project_repo.update(project_id, update_dict)
        if not success:
            raise NotFoundError(f"Project {project_id} not found or no changes made")

        ret = await self.project_repo.get_by_id(project_id)

        if update_data.collaborators:
            await self.users_repo.update_users(
                project_id, ret.admin_id, update_data.collaborators
            )

        return ret

    async def delete_project(self, project_id: str, user_id: int) -> dict:
        """(D) Каскадно видаляє проект -> сторінки -> дошки -> таски"""
        project = await self.get_project(project_id, user_id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")

        deleted_pages = 0
        deleted_boards = 0
        deleted_tasks = 0

        # 1. Ієрархічно викликаємо PageService
        for page_id in project.page_ids:
            try:
                report = await self.page_service.delete_page(page_id, user_id)
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

    async def get_full_project_for_llm(
        self, project_id: str, user_id: int
    ) -> FullProject:
        """
        Збирає (гідратує) повний JSON проекту для LLM.
        """

        project = await self.get_project(project_id, user_id)
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

    async def get_project_price_report(
        self, project_id: str, user_id: int
    ) -> ProjectPriceReport:
        """
        Розраховує фінансовий звіт для проекту,
        делегуючи роботу сервісу сторінок.
        """
        project = await self.get_project(project_id, user_id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")

        project_total_cost = 0.0
        pages_reports = []

        for page_id in project.page_ids:
            try:
                page_report = await self.page_service.get_page_price_report(
                    page_id, user_id
                )
                pages_reports.append(page_report)
                project_total_cost += page_report.overall

            except NotFoundError:
                pass

        if project.cost != project_total_cost:
            await self.project_repo.update(project.id, {"cost": project_total_cost})

        return ProjectPriceReport(
            project_id=project.id,
            project_name=project.name,
            overall=project_total_cost,
            per_page=pages_reports,
        )
