from typing import List, Optional, Union

from pydantic import BaseModel, Field, model_validator


class MainCRUDModel(BaseModel):
    user_id: int


class Collaborator(BaseModel):
    user_id: int
    role: str
    salary: float


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
    date_of_creation: str
    custom_fields: List[dict]


class BoardTemplate(MainCRUDModel):
    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str
    page_id: str
    name: str
    description: str
    priority: str
    date_of_creation: str
    tasks: List[Union[str | TaskTemplate]]


class PageTemplate(MainCRUDModel):
    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str
    name: str
    description: str
    date_of_creation: str
    boards: List[Union[str | BoardTemplate]]


class ProjectEdit(MainCRUDModel):
    id: str = Field(alias="_id")
    admin_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    collaborators: Optional[List[dict]] = None
    price: Optional[float] = None
    date_of_creation: Optional[str] = None
    pages: Optional[List[Union[str | PageTemplate]]] = None

    @model_validator(mode="before")
    def check_at_least_one(cls, values):
        fields_to_check = [
            "admin_id",
            "name",
            "description",
            "collaborators",
            "price",
            "date_of_creation",
            "pages",
        ]
        if not any(values.get(field) is not None for field in fields_to_check):
            raise ValueError("At least one editable field must be provided")
        return values


class ProjectTemplate(MainCRUDModel):
    id: Optional[str] = Field(default=None, alias="_id")
    admin_id: int
    name: str
    description: str
    collaborators: List[dict]
    price: float
    date_of_creation: str
    pages: List[Union[str | PageTemplate]]
