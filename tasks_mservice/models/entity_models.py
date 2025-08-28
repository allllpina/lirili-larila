from typing import ClassVar, List, Optional, Union

from pydantic import BaseModel, Field, model_validator


class MainCRUDModel(BaseModel):
    user_id: int


class Collaborator(BaseModel):
    user_id: int
    role: str
    salary: float


class EditModel:
    fields_to_check: ClassVar[list[str]] = []

    @model_validator(mode="before")
    def check_at_least_one(cls, values):
        if not any(values.get(field) is not None for field in cls.fields_to_check):
            raise ValueError("At least one editable field must be provided")
        return values


class TaskEdit(MainCRUDModel, EditModel):
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
    ]

    id: str = Field(alias="_id")
    name: str
    description: str
    collaborators: List[Collaborator]
    price: float
    priority: str
    status: str
    tags: List[str]
    time_to_complete: float
    custom_fields: List[dict]


class TaskTemplate(MainCRUDModel):
    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str
    name: str
    description: str
    collaborators: List[Collaborator]
    price: float
    priority: str
    status: str
    tags: List[str]
    time_to_complete: float
    date_of_creation: str
    custom_fields: List[dict]


class BoardEdit(MainCRUDModel, EditModel):
    fields_to_check: ClassVar[list[str]] = ["name", "description", "priority", "tasks"]

    id: str = Field(alias="_id")
    name: str
    description: str
    priority: str
    tasks: List[Union[str | TaskTemplate]]


class BoardTemplate(MainCRUDModel):
    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str
    name: str
    description: str
    priority: str
    date_of_creation: str
    tasks: List[Union[str | TaskTemplate]]


class PageEdit(MainCRUDModel, EditModel):
    fields_to_check: ClassVar[list[str]] = ["name", "description", "boards"]

    id: str = Field(alias="_id")
    name: str
    description: str
    boards: List[Union[str | BoardTemplate]]


class PageTemplate(MainCRUDModel):
    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str
    name: str
    description: str
    date_of_creation: str
    boards: List[Union[str | BoardTemplate]]


class ProjectEdit(MainCRUDModel, EditModel):
    fields_to_check: ClassVar[list[str]] = [
        "name",
        "description",
        "collaborators",
        "price",
        "pages",
    ]

    id: str = Field(alias="_id")
    name: Optional[str] = None
    description: Optional[str] = None
    collaborators: Optional[List[dict]] = None
    price: Optional[float] = None
    pages: Optional[List[Union[str | PageTemplate]]] = None


class ProjectTemplate(MainCRUDModel):
    id: Optional[str] = Field(default=None, alias="_id")
    admin_id: int
    name: str
    description: str
    collaborators: List[dict]
    price: float
    date_of_creation: str
    pages: List[Union[str | PageTemplate]]
