from typing import Optional

from pydantic import BaseModel


class TaskTemplate(BaseModel):
    _id: Optional[str] = None
    project_id: str
    board_id: str
    name: str
    description: str
    collaborators: list[dict]
    price: float
    priority: str
    status: str
    tags: list[str]
    time_to_complete: float
    date_of_creation: str
    custom_fields: list[dict]


class BoardTemplate(BaseModel):
    _id: Optional[str] = None
    project_id: str
    page_id: str
    name: str
    description: str
    priority: str
    date_of_creation: str
    tasks: list[str | dict]


class PageTemplate(BaseModel):
    _id: Optional[str] = None
    project_id: str
    name: str
    description: str
    date_of_creation: str
    boards: list[str | dict]


class ProjectTemplate(BaseModel):
    _id: Optional[str] = None
    admin_id: int
    name: str
    descrition: str
    collaborators: list[dict]
    price: float
    date_of_creation: str
    pages: list[str | dict]
