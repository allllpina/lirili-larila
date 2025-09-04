from typing import ClassVar, List, Optional, Union

from pydantic import BaseModel, Field, model_validator


class MainCRUDModel(BaseModel):
    user_id: Optional[int] = None


class Collaborator(BaseModel):
    user_id: int
    role: str
    salary: float


class EditModel(BaseModel):
    fields_to_check: ClassVar[list[str]] = []

    @model_validator(mode="before")
    def check_at_least_one(cls, values: dict):
        if not any(key in values for key in cls.fields_to_check):
            raise ValueError("At least one editable field must be provided")
        return values


class CustomFieldMove(MainCRUDModel):
    taskGiverId: str
    taskReceiverId: str
    customField: dict


class TaskMove(MainCRUDModel):
    boardGiverId: str
    boardReceiverId: str
    taskId: str


class TaskEdit(EditModel, MainCRUDModel):
    fields_to_check: ClassVar[list[str]] = [
        "name",
        "description",
        "collaborators",
        "price",
        "priority",
        "status",
        "tags",
        "time_to_complete",
        "custom_fields",
        "id",
    ]

    id: Optional[str] = Field(None, alias="_id")
    name: Optional[str] = None
    description: Optional[str] = None
    collaborators: Optional[List[Collaborator]] = None
    price: Optional[float] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    time_to_complete: Optional[float] = None
    custom_fields: Optional[List[dict]] = None


class TaskTemplate(MainCRUDModel):
    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str
    board_id: str
    name: str
    description: str
    collaborators: List[Collaborator]
    price: float
    priority: str
    status: str
    tags: List[str]
    time_to_complete: float
    custom_fields: List[dict]


class BoardMove(MainCRUDModel):
    pageGiverId: str
    pageReceiverId: str
    boardId: str


class BoardEdit(EditModel, MainCRUDModel):
    fields_to_check: ClassVar[list[str]] = [
        "name",
        "description",
        "priority",
        "tasks",
        "project_id",
    ]

    project_id: Optional[str] = None
    id: Optional[str] = Field(None, alias="_id")
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    tasks: Optional[List[Union[str, TaskTemplate]]] = None


class BoardTemplate(MainCRUDModel):
    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str
    page_id: str
    name: str
    description: str
    priority: str
    tasks: List[Union[str, TaskTemplate]]


class PageEdit(EditModel, MainCRUDModel):
    fields_to_check: ClassVar[list[str]] = ["name", "description", "boards", "id"]

    id: Optional[str] = Field(None, alias="_id")
    name: Optional[str] = None
    description: Optional[str] = None
    boards: Optional[List[Union[str, BoardTemplate]]] = None


class PageTemplate(MainCRUDModel):
    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str
    name: str
    description: str
    boards: List[Union[str, BoardTemplate]]


class ProjectEdit(EditModel, MainCRUDModel):
    fields_to_check: ClassVar[list[str]] = [
        "name",
        "description",
        "collaborators",
        "price",
        "pages",
        "id",
    ]

    id: Optional[str] = Field(None, alias="_id")
    name: Optional[str] = None
    description: Optional[str] = None
    collaborators: Optional[List[dict]] = None
    price: Optional[float] = None
    pages: Optional[List[Union[str, PageTemplate]]] = None


class ProjectTemplate(MainCRUDModel):
    id: Optional[str] = Field(default=None, alias="_id")
    admin_id: int
    name: str
    description: str
    collaborators: List[dict]
    price: float
    pages: List[Union[str, PageTemplate]]
