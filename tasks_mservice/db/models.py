from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class Collaborator(BaseModel):
    usr_id: int
    role: str
    salary: float


class Deadline(BaseModel):
    type: Literal["deadline_date"]
    date: str
    is_expired: bool


class Checkbox(BaseModel):
    type: Literal["checkbox"]
    checked: bool
    text: str


class Text(BaseModel):
    type: Literal["text"]
    text: str


class Dropdown(BaseModel):
    type: Literal["dropdown"]
    elements: List[str]
    index_of_selected: int


CustomField = Annotated[
    Union[Deadline, Checkbox, Text, Dropdown], Field(discriminator="type")
]


class TaskDocument(BaseModel):
    """Модель, що описує документ в колекції 'tasks'"""

    id: str = Field(..., alias="_id")
    project_id: str
    board_id: str
    name: str
    description: str
    collaborators: List[Collaborator]

    priority: Literal["low", "medium", "high", "None"]
    status: Literal["complete", "in progress", "not done"]
    tags: List[str]

    custom_fields: List[CustomField]
    time_to_complete: Optional[float] = None

    class Config:
        populate_by_name = True


class BoardDocument(BaseModel):
    """Модель, що описує документ в колекції 'boards'"""

    id: str = Field(..., alias="_id")
    project_id: str
    page_id: str
    name: str
    description: str
    task_ids: List[str] = []

    class Config:
        populate_by_name = True


class PageDocument(BaseModel):
    """Модель, що описує документ в колекції 'pages'"""

    id: str = Field(..., alias="_id")
    project_id: str
    name: str
    description: str
    board_ids: List[str] = []

    class Config:
        populate_by_name = True


class ProjectDocument(BaseModel):
    """Модель, що описує документ в колекції 'projects'"""

    id: str = Field(..., alias="_id")
    admin_id: int
    name: str
    description: str
    collaborators: List[Collaborator]

    page_ids: List[str] = []

    class Config:
        populate_by_name = True
