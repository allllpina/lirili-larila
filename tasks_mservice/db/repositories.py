from typing import List, Optional

from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.results import DeleteResult, UpdateResult

from .models import (
    BoardDocument,
    Collaborator,
    PageDocument,
    ProjectDocument,
    TaskDocument,
)


class TaskRepository:
    """Керує колекцією 'tasks' АСИНХРОННО"""

    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.get_collection("tasks")

    async def get_by_id(self, task_id: str) -> Optional[TaskDocument]:
        data = await self.collection.find_one({"_id": task_id})
        return TaskDocument.model_validate(data) if data else None

    async def create(self, task_data: dict) -> TaskDocument:
        await self.collection.insert_one(task_data)
        return TaskDocument.model_validate(task_data)

    async def delete(self, task_id: str) -> bool:
        result: DeleteResult = await self.collection.delete_one({"_id": task_id})
        return result.deleted_count > 0

    async def update(self, doc_id: str, update_data: dict) -> bool:
        """
        Загальний метод оновлення.
        'update_data' - це словник з полями для $set.
        """
        result: UpdateResult = await self.collection.update_one(
            {"_id": doc_id}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def get_by_board_id(self, board_id: str) -> list[TaskDocument]:
        cursor = self.collection.find({"board_id": board_id})
        return [TaskDocument.model_validate(doc) async for doc in cursor]

    async def delete_by_board_id(self, board_id: str) -> int:
        result: DeleteResult = await self.collection.delete_many({"board_id": board_id})
        return result.deleted_count

    async def update_board_id(self, task_id: str, new_board_id: str) -> bool:
        result: UpdateResult = await self.collection.update_one(
            {"_id": task_id}, {"$set": {"board_id": new_board_id}}
        )
        return result.modified_count > 0


class BoardRepository:
    """Керує колекцією 'boards' АСИНХРОННО"""

    def __init__(self, db: AsyncDatabase):
        self.collection = db.get_collection("boards")

    async def get_by_id(self, board_id: str) -> Optional[BoardDocument]:
        data = await self.collection.find_one({"_id": board_id})
        return BoardDocument.model_validate(data) if data else None

    async def create(self, board_data: dict) -> BoardDocument:
        await self.collection.insert_one(board_data)
        return BoardDocument.model_validate(board_data)

    async def delete(self, board_id: str) -> bool:
        result: DeleteResult = await self.collection.delete_one({"_id": board_id})
        return result.deleted_count > 0

    async def update(self, doc_id: str, update_data: dict) -> bool:
        """
        Загальний метод оновлення.
        'update_data' - це словник з полями для $set.
        """
        result: UpdateResult = await self.collection.update_one(
            {"_id": doc_id}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def get_by_page_id(self, page_id: str) -> List[BoardDocument]:
        cursor = self.collection.find({"page_id": page_id})
        return [BoardDocument.model_validate(doc) async for doc in cursor]

    async def delete_by_page_id(self, page_id: str) -> int:
        result: DeleteResult = await self.collection.delete_many({"page_id": page_id})
        return result.deleted_count

    async def add_task_id(self, board_id: str, task_id: str):
        result: UpdateResult = await self.collection.update_one(
            {"_id": board_id}, {"$push": {"task_ids": task_id}}
        )
        return result.modified_count > 0

    async def remove_task_id(self, board_id: str, task_id: str):
        result: UpdateResult = await self.collection.update_one(
            {"_id": board_id}, {"$pull": {"task_ids": task_id}}
        )
        return result.modified_count > 0


class PageRepository:
    """Керує колекцією 'pages' АСИНХРОННО"""

    def __init__(self, db: AsyncDatabase):
        self.collection = db.get_collection("pages")

    async def get_by_id(self, page_id: str) -> Optional[PageDocument]:
        data = await self.collection.find_one({"_id": page_id})
        return PageDocument.model_validate(data) if data else None

    async def create(self, page_data: dict) -> PageDocument:
        await self.collection.insert_one(page_data)
        return PageDocument.model_validate(page_data)

    async def delete(self, page_id: str) -> bool:
        result: DeleteResult = await self.collection.delete_one({"_id": page_id})
        return result.deleted_count > 0

    async def update(self, doc_id: str, update_data: dict) -> bool:
        """
        Загальний метод оновлення.
        'update_data' - це словник з полями для $set.
        """
        result: UpdateResult = await self.collection.update_one(
            {"_id": doc_id}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def get_by_project_id(self, project_id: str) -> List[PageDocument]:
        cursor = self.collection.find({"project_id": project_id})
        return [PageDocument.model_validate(doc) async for doc in cursor]

    async def delete_by_project_id(self, project_id: str) -> int:
        result: DeleteResult = await self.collection.delete_many(
            {"project_id": project_id}
        )
        return result.deleted_count

    async def add_board_id(self, page_id: str, board_id: str) -> bool:
        result: UpdateResult = await self.collection.update_one(
            {"_id": page_id}, {"$push": {"board_ids": board_id}}
        )
        return result.modified_count > 0

    async def remove_board_id(self, page_id: str, board_id: str) -> bool:
        result: UpdateResult = await self.collection.update_one(
            {"_id": page_id}, {"$pull": {"board_ids": board_id}}
        )
        return result.modified_count > 0


class ProjectRepository:
    """Керує колекцією 'projects' АСИНХРОННО"""

    def __init__(self, db: AsyncDatabase):
        self.collection = db.get_collection("projects")

    async def get_by_id(self, project_id: str) -> Optional[ProjectDocument]:
        data = await self.collection.find_one({"_id": project_id})
        return ProjectDocument.model_validate(data) if data else None

    async def create(self, project_data: dict) -> ProjectDocument:
        await self.collection.insert_one(project_data)
        return ProjectDocument.model_validate(project_data)

    async def delete(self, project_id: str) -> bool:
        result: DeleteResult = await self.collection.delete_one({"_id": project_id})
        return result.deleted_count > 0

    async def update(self, doc_id: str, update_data: dict) -> bool:
        """
        Загальний метод оновлення.
        'update_data' - це словник з полями для $set.
        """
        result: UpdateResult = await self.collection.update_one(
            {"_id": doc_id}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def get_all(self) -> List[ProjectDocument]:
        cursor = self.collection.find({})
        return [ProjectDocument.model_validate(doc) async for doc in cursor]

    async def add_page_id(self, project_id: str, page_id: str) -> bool:
        result: UpdateResult = await self.collection.update_one(
            {"_id": project_id}, {"$push": {"page_ids": page_id}}
        )
        return result.modified_count > 0

    async def remove_page_id(self, project_id: str, page_id: str) -> bool:
        result: UpdateResult = await self.collection.update_one(
            {"_id": project_id}, {"$pull": {"page_ids": page_id}}
        )
        return result.modified_count > 0

    async def get_projects_by_user(self, user_id: int) -> List[ProjectDocument]:
        """
        Знаходить усі проекти, де користувач є адміном АБО колаборатором.
        """
        query = {"$or": [{"admin_id": user_id}, {"collaborators.usr_id": user_id}]}
        cursor = self.collection.find(query)
        return [ProjectDocument.model_validate(doc) async for doc in cursor]


class UsersRepository:
    def __init__(self, db: AsyncDatabase):
        self.collection = db.get_collection("users")

    async def set_users(
        self,
        project_id: str,
        project_name: str,
        admin_id: int,
        collaborators: List[Collaborator],
    ) -> bool:
        """
        Додає користувача в БД для сепарації проектів
        """
        allowed_users = [admin_id] + [c.usr_id for c in collaborators]

        users_data = {
            "_id": project_id,
            "name": project_name,
            "users": allowed_users,
        }

        await self.collection.insert_one(users_data)

        return True

    async def update_users(
        self,
        project_id: str,
        admin_id: int,
        collaborators: List[Collaborator],
    ) -> bool:
        """
        Заміняє користувачів в БД для сепарації проектів
        """
        allowed_users = [admin_id] + [c.usr_id for c in collaborators]
        await self.collection.update_one(
            {"_id": project_id}, {"$set": {"users": allowed_users}}
        )

        return True

    async def check_access(self, project_id: str, user_id: int) -> bool:
        """
        Перевіряє, чи є користувач у списку
        """
        record = await self.collection.find_one({"_id": project_id})

        return user_id in record["users"]
