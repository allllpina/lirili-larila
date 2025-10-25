import uuid
from datetime import datetime

from entities_module.custom_fields import CustomField, custom_fields
from entities_module.interfaces import JSON_interface
from models.entity_models import Collaborator

# from pymongo import AsyncMongoClient
from pymongo.database import Database


def fields(all_fields: dict[str, type], updatable_fields: dict[str, type]):
    """Decorator which adds allowed attributes to change in class"""

    def decorator(cls: BaseEntity):
        cls.__updatable_fields__ = updatable_fields
        cls.__fields__ = all_fields
        return cls

    return decorator


class BaseEntity(JSON_interface):
    """Base class for entities"""

    # all fields
    __fields__: dict[str, type] = {}

    # all allowed attributes to be changed
    __updatable_fields__: dict[str, type] = {}

    # name of the collection in database which is used by certain child class
    __collection__: str

    # CONSTRUCTORS
    def __init__(self, db: Database):
        super().__init__()
        self.__db__ = db

    @classmethod
    async def from_template(cls, template: dict, db: Database):
        """Method which creates object from certain template"""
        self = cls(db)
        if not template.get("_id", None):
            template["_id"] = str(uuid.uuid4())
        await self.parse_dict(template=template)
        return self

    @classmethod
    async def from_db(cls, id: str, db: Database):
        """Method which creates object using record id.
        It takes template from database using this id"""
        try:
            self = cls(db)
            # make if statement if template is None
            template = await self.read_from_db(id=id)
            if template is None:
                raise RuntimeError("No such record")
            await self.parse_dict(template=template)
            return self
        except RuntimeError:
            raise RuntimeError("Something wrong with database")

    # DATABASE RELATED METHODS
    async def delete_in_db(self):
        try:
            collection = self.__db__.get_collection(self.__collection__)
            deleted = await self._pre_delete()
            await collection.delete_one({"_id": getattr(self, "_id")})

            return {
                "operation": "delete",
                "status": "complete",
                "objects_deleted": deleted,
            }
        except RuntimeError:
            raise RuntimeError("Something went wrong while deleting object")

    async def read_from_db(self, id: str) -> dict:
        try:
            collection = self.__db__.get_collection(self.__collection__)
            res = await collection.find_one({"_id": id})
            return res
        except RuntimeError:
            raise RuntimeError("Something wrong with database")

    async def write_to_db(self):
        try:
            collection = self.__db__.get_collection(self.__collection__)

            # checking if such record does exist
            res = await collection.find_one({"_id": getattr(self, "_id")})

            # dict representation of data
            data = self.dump_to_dict()

            # _pre_write method is a hook which makes all unique logic being described in child classes
            await self._pre_write()

            if res:
                await collection.replace_one({"_id": getattr(self, "_id")}, data)
            else:
                await collection.insert_one(data)

            return {
                "operation": "write",
                "status": "complete",
                "objects_writed": data,
            }

        except RuntimeError:
            raise RuntimeError("Something wrong with database")

    # GENERAL METHODS
    async def parse_dict(self, template):
        if self._check_template(template=template, necessary_keys=self.__fields__):
            self._id: str = template.get("_id")
            self.project_id: str = template.get("project_id")
            self.date_of_creation: str = template.get("date_of_creation")

            self.name: str = template.get("name")
            self.description: str = template.get("description")

            await self._parse_hook(template)
        else:
            raise ValueError("Template for entity creation is incorrect!")

    def dump_to_dict(self, full=False):
        ret: dict = {key: getattr(self, key, None) for key in self.__fields__}

        ret = self._dump_to_dict_hook(ret=ret, full=full)
        ret.pop("__db__", None)

        if isinstance(ret, dict):
            return ret
        else:
            raise TypeError("Return value is not dictionary!")

    async def update(self, **kwargs):
        """Method that allows to change attribute values
        (only ones that allowed to be changed)"""
        for key, value in kwargs.items():
            if key not in self.__updatable_fields__:
                raise AttributeError(
                    "Field '{}' is not allowed to be updated!".format(key)
                )

            expected_type = self.__updatable_fields__[key]
            if value is not None and not isinstance(value, expected_type):
                raise TypeError(
                    "Field '{}' must be type {}, got {}".format(
                        key, expected_type.__name__, type(value).__name__
                    )
                )

            setattr(self, key, value)

        await self.__db__.get_collection(self.__collection__).update_one(
            {"_id": self._id}, {"$set": kwargs}
        )
        self._update_log(self.__class__.__name__)

        return {
            "operation": "update",
            "status": "complete",
            "objects_writed": {
                "object_id": getattr(self, "_id"),
                "fields_changed": kwargs,
            },
        }

    # HOOKS
    def _dump_to_dict_hook(self, ret, full=False):
        """Hook which dumps all child instances in db"""
        pass

    async def _pre_delete(self) -> dict:
        """Hook which deletes all child instances in db"""
        pass

    async def _pre_write(self):
        """Hook which is used to make database writing flexible in child classes"""
        pass

    async def _parse_hook(self, template):
        """Hook which is used to parse unique fields for classes"""
        pass

    # SERVICE METHODS

    def _check_template(self, template: dict, necessary_keys: list):
        """Method which checks if template has a valid structure"""
        if template is None:
            return False
        try:
            for key in necessary_keys:
                if key not in template.keys():
                    return False
            return True
        except ValueError:
            ValueError("Most likely, function couldn't get template")

    async def _add_children(
        self, items, cls, collection: list, write_to_db: bool = False
    ):
        if all(isinstance(item, str) for item in items):
            # Means it's IDs in the items list
            for id in items:
                collection.append(await cls.from_db(id=id, db=self.__db__))
        elif all(isinstance(item, dict) for item in items):
            # Means it's templates in the items list
            for temp in items:
                collection.append(
                    await cls.from_template(template=temp, db=self.__db__)
                )
        else:
            raise ValueError("Invalid items format")

        if write_to_db:
            await self.write_to_db()

    # TO CHANGE IN DEVELOPMENT
    def _update_log(self, name: str):
        """Method that logging all updates"""
        print(
            "[LOG] {} was uptated {}".format(
                name, datetime.strftime(datetime.now(), "%d-%m-%y %H:%M:%S")
            )
        )


@fields(
    all_fields={
        "_id": str,
        "project_id": str,
        "date_of_creation": str,
        "name": str,
        "description": str,
        "status": str,
        "tags": list[str],
        "price": float,
        "priority": str,
        "time_to_complete": float,
        "custom_fields": list[CustomField],
        "collaborators": list[Collaborator],
    },
    updatable_fields={
        "name": str,
        "description": str,
        "status": str,
        "tags": list[str],
        "price": float,
        "priority": str,
        "time_to_complete": float,
        "custom_fields": list[CustomField],
        "collaborators": list[Collaborator],
    },
)
class Task(BaseEntity):
    __collection__ = "tasks"
    """Class for 'task' instance, contains 'custom fields' instances"""

    @property
    def id(self):
        return self._id

    async def add_custom_field(self, template: dict, write_to_db: bool = False) -> None:
        temp = template.copy()
        field_type = temp.pop("type")
        custom_field = custom_fields.get(field_type, None)

        if custom_field is None:
            raise ValueError("Template for custom fiels creation is incorrect!")

        self.custom_fields.append(custom_field(temp))

        if write_to_db:
            await self.write_to_db()

    async def _parse_hook(self, template: dict):
        self.collaborators: list[Collaborator] = template["collaborators"]
        self.status: str = template["status"]
        self.tags: list[str] = template["tags"]

        self.price: float = template["price"] if (template["price"] is not None) else -1
        self.time_to_complete: float = (
            template["time_to_complete"]
            if (template["time_to_complete"] is not None)
            else -1
        )
        self.priority: str = (
            template["priority"] if template["priority"] is not None else "None"
        )

        self.custom_fields: list[CustomField] = []
        for field in template["custom_fields"]:
            await self.add_custom_field(field)

    async def _pre_delete(self) -> str:
        return {"deleted_task": self._id}

    async def delete_custom_field(self, custom_field: dict):
        """Method which allows to delete record about custom field in task in database"""

        self.custom_fields = list(
            filter(lambda c_f: c_f != custom_field, self.custom_fields)
        )

        await self.__db__.get_collection(self.__collection__).update_one(
            {"_id": self._id}, {"$set": {"tasks": self.custom_fields}}
        )

    def _dump_to_dict_hook(self, ret, full=False):
        custom_fields_: list[str] = []

        if self.custom_fields:
            custom_fields_ = [c_f.dump_to_dict() for c_f in self.custom_fields]

        ret["custom_fields"] = custom_fields_

        return ret

    async def calculate_task_cost(self, rewrite=False) -> dict | None:
        """
        Method that calculates cost of the task regarding on time to complete.
        Calculation happens only if `Task.status` == "complete"
        """
        if self.status != "complete":
            return None

        overall_cost: float = sum(
            [
                employee.get("salary") * self.time_to_complete
                for employee in self.collaborators
            ]
        )

        per_collab: list = []

        for emploee in self.collaborators:
            empl_copy = emploee.copy()
            empl_copy["salary"] *= self.time_to_complete
            per_collab.append(emploee)

        if rewrite:
            self.price = overall_cost
            await self.write_to_db()

        return {
            "overall_cost_for_task": overall_cost,
            "task_name": self.name,
            "details": per_collab,
        }


@fields(
    all_fields={
        "_id": str,
        "project_id": str,
        "name": str,
        "description": str,
        "date_of_creation": str,
        "tasks": list[Task],
    },
    updatable_fields={
        "project_id": str,
        "name": str,
        "description": str,
        "tasks": list[Task],
    },
)
class Board(BaseEntity):
    __collection__ = "boards"
    """Class for 'board' instance, contains 'task' instances"""

    @property
    def id(self):
        return self._id

    async def add_tasks(self, tasks: list, write_to_db: bool = False):
        """Adds 'task' instance to the 'board' instance via template:
        "date_of_creation": str,
        "name": str,
        "description": str,
        "status": str,
        "tags": list[str],
        "price": float,
        "priority": str,
        "time_to_complete": float,
        "custom_fields": list[dict] (custom field templates),
        "collaborators": list[int]}} or task_id(soon)"""

        await self._add_children(
            items=tasks, cls=Task, collection=self.tasks, write_to_db=write_to_db
        )

    async def _pre_write(self):
        if self.tasks:
            for task in self.tasks:
                await task.write_to_db()

    async def _parse_hook(self, template: dict):
        self.tasks: list[Task] = []
        tasks = template.get("tasks") or []
        await self.add_tasks(tasks=tasks)

    async def delete_task(self, task_id: str, delete_in_db: bool = False):
        """Method which allows to delete record about task on board in database"""
        self.tasks = list(filter(lambda task: task.id != task_id, self.tasks))

        if delete_in_db:
            task = await Task.from_db(id=task_id, db=self.__db__)
            await task.delete_in_db()

        await self.__db__.get_collection(self.__collection__).update_one(
            {"_id": self._id}, {"$set": {"tasks": self.tasks}}
        )

    async def _pre_delete(self) -> str:
        ret = {"deleted_board": self._id, "deleted_tasks": []}
        for task in self.tasks:
            deleted_task = await task.delete_in_db()
            ret["deleted_tasks"].append(deleted_task)
        return ret

    def _dump_to_dict_hook(self, ret, full=False):
        tasks = []
        if self.tasks:
            if full:
                tasks = [task.dump_to_dict(full=full) for task in self.tasks]
            else:
                tasks = [task.id for task in self.tasks]

        ret["tasks"] = tasks

        return ret

    async def calculate_board_cost(self, rewrite=False) -> dict | None:
        overall_cost: float = 0
        per_task: list = []
        for task in self.tasks:
            task = await task.calculate_task_cost(rewrite=rewrite)
            if task is not None:
                overall_cost += task["overall_cost_for_task"]
                per_task.append(task)

        if per_task:
            return {
                "overall_cost_for_board": overall_cost,
                "board_name": self.name,
                "details": per_task,
            }
        return None


@fields(
    all_fields={
        "_id": str,
        "project_id": str,
        "name": str,
        "description": str,
        "date_of_creation": str,
        "boards": list[Board],
    },
    updatable_fields={"name": str, "description": str, "boards": list[Board]},
)
class Page(BaseEntity):
    __collection__ = "pages"
    """Class for 'page' instance, contains 'board' instances"""

    @property
    def id(self):
        return self._id

    async def add_boards(self, boards: list, write_to_db: bool = False):
        """Adds 'board' instance to the 'task' instance via template:
        "name": str,
        "description": str,
        "priority": str,
        "date_of_creation": str,
        "tasks": list[str](task IDs)} or board_id(soon)"""
        await self._add_children(
            items=boards, cls=Board, collection=self.boards, write_to_db=write_to_db
        )

    async def _pre_write(self):
        if self.boards:
            for board in self.boards:
                await board.write_to_db()

    async def _parse_hook(self, template: dict):
        self.boards: list[Board] = []
        boards = template.get("boards") or []
        await self.add_boards(boards=boards)

    async def delete_board(self, board_id: str, delete_in_db: bool = False):
        """Method which allows to delete record about board on page in database"""
        self.boards = list(filter(lambda board: board.id != board_id, self.boards))

        if delete_in_db:
            board = await Board.from_db(id=board_id, db=self.__db__)
            await board.delete_in_db()

        await self.__db__.get_collection(self.__collection__).update_one(
            {"_id": self._id}, {"$set": {"boards": self.boards}}
        )

    async def _pre_delete(self) -> str:
        ret = {"deleted_page": self._id, "deleted_boards": []}
        for board in self.boards:
            deleted_board = await board.delete_in_db()
            ret["deleted_boards"].append(deleted_board)
        return ret

    def _dump_to_dict_hook(self, ret, full=False):
        boards = []
        if self.boards:
            if full:
                boards = [board.dump_to_dict(full=full) for board in self.boards]
            else:
                boards = [board.id for board in self.boards]

        ret["boards"] = boards

        return ret

    async def calculate_page_cost(self, rewrite=False) -> dict | None:
        overall_cost: float = 0
        per_board: list = []

        for board in self.boards:
            board = await board.calculate_board_cost(rewrite=rewrite)
            if board:
                overall_cost += board["overall_cost_for_board"]
                per_board.append(board)

        if per_board:
            return {
                "overall_cost_for_page": overall_cost,
                "page_name": self.name,
                "details": per_board,
            }
        return None


@fields(
    all_fields={
        "_id": str,
        "admin_id": int,
        "name": str,
        "description": str,
        "collaborators": list[Collaborator],
        "price": int,
        "date_of_creation": str,
        "pages": list[str],
    },
    updatable_fields={
        "name": str,
        "description": str,
        "collaborators": list[Collaborator],
        "price": int,
        "pages": list[str],
    },
)
class Project(BaseEntity):
    __collection__ = "projects"
    """Class for 'project' instance, contains 'page' instances and workers"""

    @property
    def id(self):
        return self._id

    async def add_pages(self, pages: list, write_to_db: bool = False):
        """Adds 'page' instance to the 'project' instance via template:
        {"project_id": str,
        "name": str,
        "description": str,
        "date_of_creation": str,
        "boards": list[str] (list of IDs)} or page_id(soon)"""
        await self._add_children(
            items=pages, cls=Page, collection=self.pages, write_to_db=write_to_db
        )

    async def _pre_write(self):
        if self.pages:
            for page in self.pages:
                await page.write_to_db()

    async def _parse_hook(self, template: dict):
        self.admin_id: int = template["admin_id"]

        self.collaborators: list[Collaborator] = template["collaborators"]
        self.price: int = template["price"] if template["price"] is not None else -1

        self.pages: list[Page] = []
        pages = template.get("pages") or []
        await self.add_pages(pages=pages)

    async def delete_page(self, page_id: str, delete_in_db: bool = False):
        """Method which allows to delete record about page in project in database"""
        self.pages = list(filter(lambda page: page.id != page_id, self.pages))

        if delete_in_db:
            page = await Page.from_db(id=page_id, db=self.__db__)
            await page.delete_in_db()

        await self.__db__.get_collection(self.__collection__).update_one(
            {"_id": self._id}, {"$set": {"pages": self.pages}}
        )

    async def _pre_delete(self) -> str:
        ret = {"deleted_project": self._id, "deleted_pages": []}
        for page in self.pages:
            deleted_page = await page.delete_in_db()
            ret["deleted_pages"].append(deleted_page)
        return ret

    def _dump_to_dict_hook(self, ret, full=False):
        pages = []
        if self.pages:
            if full:
                pages = [page.dump_to_dict(full=full) for page in self.pages]
            else:
                pages = [page.id for page in self.pages]

        ret["pages"] = pages
        return ret

    async def calculate_project_cost(self, rewrite=False) -> dict:
        overall_cost: float = 0
        per_page: list = []

        for page in self.pages:
            page = await page.calculate_page_cost(rewrite=rewrite)
            if page:
                overall_cost += page["overall_cost_for_page"]
                per_page.append(page)

        if rewrite:
            self.price = overall_cost
            await self.write_to_db()

        if per_page:
            return {
                "overall_cost_for_project": overall_cost,
                "page_name": self.name,
                "details": per_page,
            }
        return {
            "Error": "Unable to calculate project cost, most likely because `time_to_complete` isn't set"
        }
