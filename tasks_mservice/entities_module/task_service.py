from typing import List, Tuple

from db.models import TaskDocument
from db.repositories import TaskRepository
from models.entity_schemas import CollaboratorCostInfo, TaskUpdate

from .exceptions import BusinessLogicError, NotFoundError


class TaskService:
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    async def get_task_by_id(self, task_id: str) -> TaskDocument:
        """(R) Отримує один таск"""
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError(f"Task {task_id} not found")
        return task

    async def update_task(self, task_id: str, update_data: TaskUpdate) -> TaskDocument:
        """(U) Оновлює таск"""
        # .model_dump(exclude_unset=True) генерує dict
        # тільки з тими полями, які передав клієнт
        update_dict = update_data.model_dump(exclude_unset=True)

        if not update_dict:
            raise BusinessLogicError("No fields to update")

        success = await self.task_repo.update(task_id, update_dict)

        if not success:
            raise NotFoundError(f"Task {task_id} not found or no changes made")

        return await self.get_task_by_id(task_id)

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
