import json
import uuid
from datetime import datetime

from pymongo import AsyncMongoClient

from interfaces import JSON_interface
from custom_fields import *

# Temporary vars
DATABASE_HOST = 'localhost'
DATABASE_PORT = 27017
DATABASE_NAME = 'entities'

def fields(all_fields: dict[str, type], updatable_fields: dict[str, type]):
    """Decorator which adds allowed attributes to change in class"""
    typeErr = TypeError("Function returned wrong data type")
    def decorator(cls: BaseEntity):
        cls.__updatable_fields__ = updatable_fields
        cls.__fields__ = all_fields
        return cls
       
    return decorator


class BaseEntity(JSON_interface):
    """Base class for entities"""
    __fields__: dict[str, type] = {} # all fields
    __updatable_fields__: dict[str, type] = {} # all allowed attributes to be changed

    def __init__(self, template: dict = None):
        super().__init__()
        if not template.get("_id", None):
            template["_id"] = str(uuid.uuid4())

        self.parse_dict(template=template)
            
    def check_template(self, template: dict, necessary_keys: list):
        """Method which checks if template has a valid structure"""
        for key in necessary_keys:
            if key not in template.keys():
                return False
        return True
    
        

    def update(self, **kwargs):
        """Method that allows to change attribute values (only ones that allowed to)"""
        for key, value in kwargs.items():
            if key not in self.__updatable_fields__:
                raise AttributeError(f"Field '{key}' is not allowed to be updated!")
            
            expected_type = self.__updatable_fields__[key]
            if value is not None and not isinstance(value, expected_type):
                raise TypeError(f"Field '{key}' must be type {expected_type.__name__}, got {type(value).__name__}")
            
            setattr(self, key, value)
        self.update_log(self.__class__.__name__)

    def get_from_db(self, id: str, db) -> dict:
        pass

    # TO CHANGE IN DEVELOPMENT
    def update_log(self, name:str):
        """Method that logging all updates"""
        print(f"[LOG] {name} was uptated {datetime.strftime(datetime.now(), "%d-%m-%y %H:%M:%S")}")


@fields(all_fields = {
    "_id": str,
    "board_id": str,
    "date_of_creation": str,
    "name": str,
    "description": str,
    "status": str,
    "tags": list[str],
    "price": float,
    "priority": str,
    "time_to_complete": float,
    "custom_fields": list[CustomField],
    "collaborators": list[int]
},
        updatable_fields = {
    "name": str,
    "board_id": str,
    "description": str,
    "status": str,
    "tags": list[str],
    "price": float,
    "priority": str,
    "time_to_complete": float,
    "custom_fields": list[CustomField],
    "collaborators": list[int]
})
class Task(BaseEntity):
    """Class for 'task' instance, contains 'custom fields' instances"""
    def __init__(self, template: dict):
        super().__init__(template=template)

    @property
    def id(self):
        return self._id


    def add_collaborator(self, collaborator: dict) -> None:
        """Add a new collaborator by dict: {'usr_id': int, 'role': str, 'salary': float}"""
        self.collaborators.append(collaborator)


    def add_custom_field(self, template: dict) -> None:
        temp = template.copy()
        field_type = temp.pop('type')
        custom_field = custom_fields.get(field_type, None)
        if custom_field is None:
            print(field_type)
            raise ValueError("Template for custom fiels creation is incorrect!")
        self.custom_fields.append(custom_field(temp))


    def parse_dict(self, template: dict):
        if self.check_template(template=template, necessary_keys=self.__fields__):
            self._id: str = template["_id"] # Change regarding on MongoDB requirements
            self.board_id: str = template['board_id']
            self.date_of_creation: str = template['date_of_creation']

            self.name: str = template['name']
            self.description: str = template['description']
            self.collaborators: list[dict] = template['collaborators']
            self.status: str = template['status']
            self.tags: list[str] = template['tags']

            self.price: float = template['price'] if template['price'] > 0 else None
            self.time_to_complete: float = template['time_to_complete'] if template['time_to_complete'] > 0 else None
            self.priority: str = template['priority'] if template['priority'] != "None" else None


            self.custom_fields: list[CustomField] = []
            for field in template['custom_fields']:
                self.add_custom_field(field)

        else:
            raise ValueError("Template for entity creation is incorrect!")


    def dump_to_dict(self):
        custom_fields: list[dict] = [c_f.dump_to_dict() for c_f in self.custom_fields]

        ret: dict = self.__dict__
        ret['custom_fields'] = custom_fields

        if isinstance(ret, dict):
            return self.__dict__
        else:
            raise TypeError(f"Return value is not dictionary!")
        


@fields(all_fields={
    "_id": str,
    "page_id": str,
    "name": str,
    "description": str,
    "priority": str,
    "date_of_creation": str,
    "tasks": list[Task]
},
        updatable_fields={
    "page_id": str,
    "name": str,
    "description": str,
    "priority": str,
    "tasks": list[Task]
        }
)
class Board(BaseEntity):
    """Class for 'board' instance, contains 'task' instances"""
    def __init__(self, template: dict):
        super().__init__(template=template)

    @property
    def id(self):
        return self._id

    def add_task(self, task_template: dict = None , task_ids: list[str] = None):
        """Adds 'task' instance to the 'board' instance via template: {"board_id": str, "date_of_creation": str, "name": str, "description": str, "status": str, "tags": list[str], "price": float, "priority": str, "time_to_complete": float, "custom_fields": list[dict] (custom field templates), "collaborators": list[int]}} or task_id(soon)"""
        if task_ids is not None:
            '''Huge problem indeed, we need database first'''
            # Database needed
            pass
        elif task_template is not None:
            self.tasks.append(Task(task_template))
        else:
            raise ValueError("Neither task template nor task id wasn't given!")

    def parse_dict(self, template: dict):
        if self.check_template(template= template, necessary_keys=self.__fields__):
            self._id: str = template["_id"] # Change regarding on MongoDB requirements

            self.page_id: str = template['page_id']
            self.date_of_creation: str = template['date_of_creation']

            self.name: str = template['name']
            self.description: str = template['description']
            self.priority: str = template['priority']

            self.tasks: list[Task] = self.add_task(task_ids=template['tasks'])
        else:
            raise ValueError("Template for entity creation is incorrect!")
        
    def dump_to_dict(self):
        tasks: list[str] = [task.id for task in self.tasks]

        ret: dict = self.__dict__
        ret['tasks'] = tasks

        if isinstance(ret, dict):
            return self.__dict__
        else:
            raise TypeError(f"Return value is not dictionary!")
        

@fields(all_fields={
    "_id": str,
    "project_id": str,
    "name": str,
    "description": str,
    "date_of_creation": str,
    "boards": list[Board]
},
        updatable_fields={
    "name": str,
    "description": str,
    "boards": list[Board]
        }    
)
class Page(BaseEntity):
    """Class for 'page' instance, contains 'board' instances"""
    def __init__(self, template: dict):
        super().__init__(template= template)

    @property
    def id(self):
        return self._id
    
    def add_board(self, board_template: dict = None, board_ids: list = None):
        """Adds 'board' instance to the 'task' instance via template: {"page_id": str, "name": str, "description": str, "priority": str, "date_of_creation": str, "tasks": list[str](task IDs)} or board_id(soon)"""
        if board_ids is not None:
            '''Huge problem indeed, we need database first'''
            # Database needed
            pass
        elif board_template is not None:
            self.tasks.append(Task(board_template))
        else:
            raise ValueError("Neither task template nor task id wasn't given!")

    def parse_dict(self, template: dict):
        if self.check_template(template= template, necessary_keys= self.__fields__):
            self._id: str = template["_id"] # Change regarding on MongoDB requirements

            self.project_id:str = template['project_id']
            self.date_of_creation: str = template['date_of_creation']

            self.name: str = template['name']
            self.description: str = template['description']

            self.boards: list[Board] = self.add_board(board_ids=template['pages'])
        else:
            raise ValueError("Template for entity creation is incorrect!")
        
    def dump_to_dict(self):
        boards: list[str] = [board.id for board in self.boards]

        ret: dict = self.__dict__
        ret['boards'] = boards

        if isinstance(ret, dict):
            return self.__dict__
        else:
            raise TypeError(f"Return value is not dictionary!")



@fields(all_fields={
    "_id": str,
    "admin_id": int,
    "name": str,
    "description": str,
    "collaborators": list[dict],
    "price": int,
    "date_of_creation": str,
    "pages": list[str]
},
        updatable_fields={
    "name": str,
    "description": str,
    "collaborators": list[dict],
    "price": int,
    "pages": list[str]
        }
)
class Project(BaseEntity):
    """Class for 'project' instance, contains 'page' instances and workers"""
    def __init__(self, template: dict):
        super().__init__(template = template)

    @property
    def id(self):
        return self._id
    
    def add_page(self, page_template: dict = None, page_ids: list[str] = None):
        """Adds 'page' instance to the 'project' instance via template: {"project_id": str, "name": str, "description": str, "date_of_creation": str, "boards": list[str] (list of IDs)} or page_id(soon)"""
        if page_ids is not None:
            '''Huge problem indeed, we need database first'''
            # Database needed
            pass
        elif page_template is not None:
            self.tasks.append(Task(board_template))
        else:
            raise ValueError("Neither task template nor task id wasn't given!")

    def parse_dict(self, template: dict):
        if self.check_template(template=template, necessary_keys=self.__fields__):
            self._id: str = template["_id"] # Change regarding on MongoDB requirements

            self.admin_id: int = template['admin_id']
            self.date_of_creation: str = template['date_of_creation']
            
            self.name: str = template['name']
            self.description: str = template['description']
            self.collaborators: list[dict] = template['collaborators']
            self.price: int = template['price']

            self.pages: list[Page] = self.add_page(page_ids=template['pages'])
        else:
            raise  ValueError("Template for entity creation is incorrect!")


    def dump_to_dict(self):
        pages: list[str] = [page.id for page in self.pages]

        ret: dict = self.__dict__
        ret['pages'] = pages

        if isinstance(ret, dict):
            return self.__dict__
        else:
            raise TypeError(f"Return value is not dictionary!")
          

# t: Task = Task(template = {
#         '_id': 'f4ff2ec4-0790-467e-8b80-7119dd1aacc4',
#         "board_id": 1,
#         "name": "title",
#         "description": "",
#         "collaborators": [{"usr_id": 1, "role": "loh", "salary": 0}],
#         "price": -1,
#         "priority":"high",
#         "status": "done",
#         "tags": ["tag1", "tag2", "tag3"],
#         "time_to_complete" : -1,
#         "date_of_creation": "04-08-2025 16:15:56",
#         "custom_fields": [{"type": "deadline_date", "date":"04-08-2025 16:15:14", "is_expired": True}, {'type':"checkbox",'checked': True, "text": "popa"}]
#     })

# print(t.dump_to_dict())


