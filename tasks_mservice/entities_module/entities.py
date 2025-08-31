import uuid
from datetime import datetime

from entities_module.custom_fields import CustomField, custom_fields
from entities_module.interfaces import JSON_interface

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
    __collection__: str

    def __init__(self, db: Database):
        super().__init__()
        self.__db__ = db

    @classmethod
    async def from_template(cls, template: dict, db: Database):
        self = cls(db)
        if not template.get("_id", None):
            template["_id"] = str(uuid.uuid4())
        await self.parse_dict(template=template)
        return self

    @classmethod
    async def from_db(cls, id: str, db: Database):
        try:
            self = cls(db)
            # make if statement if template is None
            template = await self.read_from_db(id=id)
            await self.parse_dict(template=template)
            return self
        except RuntimeError:
            RuntimeError("Something wrong with database")

    async def delete_in_db(self):
        try:
            collection = self.__db__.get_collection(self.__collection__)
            deleted = await self.pre_delete()
            await collection.delete_one({"_id": getattr(self, "_id")})

            return {
                "operation": "delete",
                "status": "complete",
                "objects_deleted": deleted,
            }
        except RuntimeError:
            RuntimeError("Something went wrong while deleting object")

    async def pre_delete(self) -> dict:
        """Hook which deletes all child instances in db"""
        pass

    async def read_from_db(self, id: str) -> dict:
        try:
            collection = self.__db__.get_collection(self.__collection__)
            res = await collection.find_one({"_id": id})
            return res
        except RuntimeError:
            RuntimeError("Something wrong with database")

    async def write_to_db(self):
        try:
            collection = self.__db__.get_collection(self.__collection__)
            res = await collection.find_one({"_id": getattr(self, "_id")})

            await self.pre_write()

            if res:
                await collection.replace_one(
                    {"_id": getattr(self, "_id")}, self.dump_to_dict()
                )
            else:
                await collection.insert_one(self.dump_to_dict())

            return True

        except RuntimeError:
            RuntimeError("Something wrong with database")

    async def pre_write(self):
        """Hook that used to make database writing flexible in child classes"""
        pass

    def check_template(self, template: dict, necessary_keys: list):
        """Method which checks if template has a valid structure"""
        try:
            for key in necessary_keys:
                if key not in template.keys():
                    return False
            return True
        except ValueError:
            ValueError("Most likely, function couldn't get template")

    async def update(self, **kwargs):
        """Method that allows to change attribute values
        (only ones that allowed to)"""
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

        await self.write_to_db()
        self.update_log(self.__class__.__name__)

    # TO CHANGE IN DEVELOPMENT
    def update_log(self, name: str):
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
        "collaborators": list[int],
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
        "collaborators": list[int],
    },
)
class Task(BaseEntity):
    __collection__ = "tasks"
    """Class for 'task' instance, contains 'custom fields' instances"""

    @property
    def id(self):
        return self._id

    def add_collaborator(self, collaborator: dict) -> None:
        """Add a new collaborator by dict:
        {'usr_id': int, 'role': str, 'salary': float}"""
        self.collaborators.append(collaborator)

    async def add_custom_field(self, template: dict, write_to_db: bool = False) -> None:
        temp = template.copy()
        field_type = temp.pop("type")
        custom_field = custom_fields.get(field_type, None)

        if custom_field is None:
            print(field_type)
            raise ValueError("Template for custom fiels creation is incorrect!")

        self.custom_fields.append(custom_field(temp))

        if write_to_db:
            await self.write_to_db()

    async def parse_dict(self, template: dict):
        if self.check_template(template=template, necessary_keys=self.__fields__):
            # Change regarding on MongoDB requirements
            self._id: str = template["_id"]
            self.project_id: str = template["project_id"]
            self.date_of_creation: str = template["date_of_creation"]

            self.name: str = template["name"]
            self.description: str = template["description"]
            self.collaborators: list[dict] = template["collaborators"]
            self.status: str = template["status"]
            self.tags: list[str] = template["tags"]

            self.price: float = (
                template["price"] if (template["price"] is not None) else -1
            )
            self.time_to_complete: float = (
                template["time_to_complete"]
                if (template["time_to_complete"] is not None)
                else -1
            )
            self.priority: str = (
                template["priority"] if template["priority"] is not None else -1
            )

            self.custom_fields: list[CustomField] = []
            for field in template["custom_fields"]:
                await self.add_custom_field(field)

        else:
            raise ValueError("Template for entity creation is incorrect!")

    async def pre_delete(self) -> str:
        return {"deleted_task": self._id}

    def dump_to_dict(self):
        ret: dict = self.__dict__.copy()
        custom_fields_: list[str] = []

        if self.custom_fields:
            custom_fields_ = [c_f.dump_to_dict() for c_f in self.custom_fields]

        ret["custom_fields"] = custom_fields_
        ret.pop("__db__", None)

        if isinstance(ret, dict):
            return ret
        else:
            raise TypeError("Return value is not dictionary!")


@fields(
    all_fields={
        "_id": str,
        "project_id": str,
        "name": str,
        "description": str,
        "priority": str,
        "date_of_creation": str,
        "tasks": list[Task],
    },
    updatable_fields={
        "project_id": str,
        "name": str,
        "description": str,
        "priority": str,
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

        print(tasks)
        if all(isinstance(task, str) for task in tasks):
            """Huge problem indeed, we need database first"""
            # Database needed
            for id in tasks:
                self.tasks.append(await Task.from_db(id=id, db=self.__db__))

        elif all(isinstance(task, dict) for task in tasks):
            for temp in tasks:
                self.tasks.append(
                    await Task.from_template(template=temp, db=self.__db__)
                )
        else:
            raise ValueError("Neither task template nor task id wasn't given!")

        if write_to_db:
            await self.write_to_db()

    async def pre_write(self):
        try:
            if self.tasks:
                for task in self.tasks:
                    await task.write_to_db()
        except RuntimeError:
            RuntimeError("Task writing to db went wrong!")

    async def parse_dict(self, template: dict):
        if self.check_template(template=template, necessary_keys=self.__fields__):
            # Change regarding on MongoDB requirements
            self._id: str = template["_id"]
            self.project_id: str = template["project_id"]

            self.date_of_creation: str = template["date_of_creation"]

            self.name: str = template["name"]
            self.description: str = template["description"]
            self.priority: str = template["priority"]

            self.tasks: list[Task] = []
            tasks = template.get("tasks") or []
            await self.add_tasks(tasks=tasks)
        else:
            raise ValueError("Template for entity creation is incorrect!")

    async def pre_delete(self) -> str:
        ret = {"deleted_board": self._id, "deleted_tasks": []}
        for task in self.tasks:
            deleted_task = await task.delete_in_db()
            ret["deleted_tasks"].append(deleted_task)
        return ret

    def dump_to_dict(self):
        ret: dict = self.__dict__.copy()
        tasks = []
        if self.tasks:
            tasks = [task.id for task in self.tasks]

        ret["tasks"] = tasks
        ret.pop("__db__", None)

        if isinstance(ret, dict):
            return ret
        else:
            raise TypeError("Return value is not dictionary!")


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
        if all(isinstance(board, str) for board in boards):
            for id in boards:
                self.boards.append(await Board.from_db(id=id, db=self.__db__))
        elif all(isinstance(board, dict) for board in boards):
            for temp in boards:
                self.boards.append(
                    await Board.from_template(template=temp, db=self.__db__)
                )
        else:
            raise ValueError("Neither task template nor task id wasn't given!")

        if write_to_db:
            await self.write_to_db()

    async def pre_write(self):
        try:
            if self.boards:
                for board in self.boards:
                    await board.write_to_db()
        except RuntimeError:
            RuntimeError("Board writing to db went wrong!")

    async def parse_dict(self, template: dict):
        if self.check_template(template=template, necessary_keys=self.__fields__):
            # Change regarding on MongoDB requirements
            self._id: str = template["_id"]

            self.project_id: str = template["project_id"]
            self.date_of_creation: str = template["date_of_creation"]

            self.name: str = template["name"]
            self.description: str = template["description"]

            self.boards: list[Board] = []
            boards = template.get("boards") or []
            await self.add_boards(boards=boards)

        else:
            raise ValueError("Template for entity creation is incorrect!")

    async def pre_delete(self) -> str:
        ret = {"deleted_page": self._id, "deleted_boards": []}
        for board in self.boards:
            deleted_board = await board.delete_in_db()
            ret["deleted_boards"].append(deleted_board)
        return ret

    def dump_to_dict(self):
        ret: dict = self.__dict__.copy()
        boards = []
        if self.boards:
            boards = [board.id for board in self.boards]

        ret["boards"] = boards
        ret.pop("__db__", None)

        if isinstance(ret, dict):
            return ret
        else:
            raise TypeError("Return value is not dictionary!")


@fields(
    all_fields={
        "_id": str,
        "admin_id": int,
        "name": str,
        "description": str,
        "collaborators": list[dict],
        "price": int,
        "date_of_creation": str,
        "pages": list[str],
    },
    updatable_fields={
        "name": str,
        "description": str,
        "collaborators": list[dict],
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
        if all(isinstance(page, str) for page in pages):
            for id in pages:
                self.pages.append(await Page.from_db(id=id, db=self.__db__))
        elif all(isinstance(page, dict) for page in pages):
            for temp in pages:
                self.pages.append(
                    await Page.from_template(template=temp, db=self.__db__)
                )
        else:
            raise ValueError("Neither task template nor task id wasn't given!")

        if write_to_db:
            await self.write_to_db()

    async def pre_write(self):
        try:
            if self.pages:
                for page in self.pages:
                    await page.write_to_db()
        except RuntimeError:
            RuntimeError("Page writing to db went wrong!")

    async def parse_dict(self, template: dict):
        if self.check_template(template=template, necessary_keys=self.__fields__):
            # Change regarding on MongoDB requirements
            self._id: str = template["_id"]

            self.admin_id: int = template["admin_id"]
            self.date_of_creation: str = template["date_of_creation"]

            self.name: str = template["name"]
            self.description: str = template["description"]
            self.collaborators: list[dict] = template["collaborators"]
            self.price: int = template["price"] if template["price"] is not None else -1

            self.pages: list[Page] = []
            pages = template.get("pages") or []
            await self.add_pages(pages=pages)

        else:
            raise ValueError("Template for entity creation is incorrect!")

    async def pre_delete(self) -> str:
        ret = {"deleted_project": self._id, "deleted_pages": []}
        for page in self.pages:
            deleted_page = await page.delete_in_db()
            ret["deleted_bpages"].append(deleted_page)
        return ret

    def dump_to_dict(self):
        ret: dict = self.__dict__.copy()
        pages = []
        if self.pages:
            pages = [page.id for page in self.pages]

        ret["pages"] = pages
        ret.pop("__db__", None)

        if isinstance(ret, dict):
            return ret
        else:
            raise TypeError("Return value is not dictionary!")
