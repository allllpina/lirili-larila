import json
import uuid
from datetime import datetime


from interfaces import JSON_interface
from custom_fields import *

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

    def __init__(self, template: dict, template_id: str = None):
        super().__init__()
        if template_id is None:
            template_id = str(uuid.uuid4())
        self.parse_dict(template=template, template_id = template_id)
            
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

    # TO CHANGE IN DEVELOPMENT
    def update_log(self, name:str):
        """Method that logging all updates"""
        print(f"[LOG] {name} was uptated {datetime.strftime(datetime.now(), "%d-%m-%y %H:%M:%S")}")


@fields(all_fields = {
    "id": str,
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
    def __init__(self, template_id: str, template: dict):
        super().__init__(template=template, template_id = template_id)


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


    def parse_dict(self, template_id: str, template: dict):
        necessery_keys = [key for key in self.__fields__.keys() if key != 'id']
        if self.check_template(template=template, necessary_keys=necessery_keys):
            self.id: str = template_id
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
        custom_fields: list[CustomField] = []

        for c_f in self.custom_fields:
            custom_fields.append(c_f.dump_to_dict())

        ret = self.__dict__
        ret['custom_fields'] = custom_fields

        if isinstance(ret, dict):
            return self.__dict__
        else:
            raise TypeError(f"Return value is not dictionary!")
        



class Board(JSON_interface):
    """Class for 'board' instance, contains 'task' instances"""
    pass


# Переробити під BaseEntity!!!!!!!!!!!!!
class Page(JSON_interface):
    """Class for 'page' instance, contains 'board' instances"""
    pass


# Переробити під BaseEntity!!!!!!!!!!!!!
class Project(JSON_interface):
    """Class for 'project' instance, contains 'page' instances and workers"""
    pass


# t = Task(template = {
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
#     }, template_id = '23')



