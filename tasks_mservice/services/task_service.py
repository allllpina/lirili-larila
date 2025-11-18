from typing import List, Tuple

from api.schemas import CollaboratorCostInfo, TaskUpdate
from db.models import TaskDocument
from db.repositories import TaskRepository
from pymongo.asynchronous.database import AsyncDatabase
from utils.check_access import check_if_accessable

from .exceptions import BusinessLogicError, NotFoundError, PermissionDeniedError


class TaskService:
    def __init__(self, task_repo: TaskRepository, db: AsyncDatabase):
        self.task_repo = task_repo
        self.db = db

    async def _ensure_access(self, user_id: int, project_id: str):
        """Внутрішній метод перевірки доступу."""
        has_access = await check_if_accessable(user_id, project_id, self.db)
        if not has_access:
            raise PermissionDeniedError(
                f"User {user_id} does not have access to project {project_id}"
            )

    async def get_task(self, task_id: str, user_id: int) -> TaskDocument:
        """(R) Отримує один таск"""
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError(f"Task {task_id} not found")

        await self._ensure_access(user_id, task.project_id)
        return task

    async def update_task(
        self, task_id: str, update_data: TaskUpdate, user_id: int
    ) -> TaskDocument:
        """(U) Оновити таск із перевіркою доступу."""
        # 1. Спочатку дістаємо таск, щоб дізнатись project_id
        _ = await self.get_task(task_id, user_id)

        # 2. Перевіряємо, чи є дані для оновлення
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            raise BusinessLogicError("No fields to update provided")

        # 3. Оновлюємо
        success = await self.task_repo.update(
            task_id, update_dict
        )  # Переконайся, що додав update в репо!
        if not success:
            # Рідкісний кейс, якщо таск видалили між читанням і записом
            raise NotFoundError(f"Task {task_id} could not be updated")

        # 4. Повертаємо оновлений документ
        return await self.task_repo.get_by_id(task_id)

    # (D) Delete для таска буде в BoardService (бо таск не може існувати без дошки)

    def calculate_task_price_details(
        self, task: TaskDocument
    ) -> Tuple[float, List[CollaboratorCostInfo]]:
        """Обчислює ціну таска (для звітів)"""
        if task.status != "complete" or task.time_to_complete is None:
            return (0.0, [])

        total_cost = 0.0
        cost_breakdown_list = []

        for collab in task.collaborators:
            pay = collab.salary * task.time_to_complete
            total_cost += pay

            cost_breakdown_list.append(
                CollaboratorCostInfo(
                    usr_id=collab.usr_id,
                    hourly_rate=collab.salary,
                    hours_worked=task.time_to_complete,
                    total_pay=pay,
                )
            )

        return (total_cost, cost_breakdown_list)
