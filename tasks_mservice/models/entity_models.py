from typing import Annotated, ClassVar, List, Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator


class Collaborator(BaseModel):
    usr_id: int
    role: str
    salary: float


class EditModel(BaseModel):
    project_id: str
    fields_to_check: ClassVar[list[str]] = []

    @model_validator(mode="before")
    def check_at_least_one(cls, values: dict):
        if not any(key in values for key in cls.fields_to_check):
            raise ValueError("At least one editable field must be provided")
        return values


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


class CustomFieldMove(BaseModel):
    project_id: str
    taskGiverId: str
    taskReceiverId: str
    customField: CustomField


class TaskMove(BaseModel):
    project_id: str
    boardGiverId: str
    boardReceiverId: str
    taskId: str


class TaskEdit(EditModel):
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
    custom_fields: Optional[List[CustomField]] = None


class TaskTemplate(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str
    board_id: str
    name: str
    description: str
    collaborators: List[Collaborator]
    price: float
    priority: Literal["low", "medium", "high", "None"]
    status: Literal["complete", "in progress", "not done"]
    tags: List[str]
    time_to_complete: float
    custom_fields: List[CustomField]


class BoardMove(BaseModel):
    project_id: str
    pageGiverId: str
    pageReceiverId: str
    boardId: str


class BoardEdit(EditModel):
    fields_to_check: ClassVar[list[str]] = [
        "name",
        "description",
        "tasks",
        "project_id",
    ]

    project_id: Optional[str] = None
    id: Optional[str] = Field(None, alias="_id")
    name: Optional[str] = None
    description: Optional[str] = None
    tasks: Optional[List[Union[str, TaskTemplate]]] = None


class BoardTemplate(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str
    page_id: str
    name: str
    description: str
    tasks: List[Union[str, TaskTemplate]]


class PageEdit(EditModel):
    fields_to_check: ClassVar[list[str]] = ["name", "description", "boards", "id"]

    id: Optional[str] = Field(None, alias="_id")
    name: Optional[str] = None
    description: Optional[str] = None
    boards: Optional[List[Union[str, BoardTemplate]]] = None


class PageTemplate(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str
    name: str
    description: str
    boards: List[Union[str, BoardTemplate]]


class ProjectEdit(EditModel):
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
    collaborators: Optional[List[Collaborator]] = None
    price: Optional[float] = None
    pages: Optional[List[Union[str, PageTemplate]]] = None


class ProjectTemplate(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    admin_id: int
    name: str
    description: str
    collaborators: List[Collaborator]
    price: float
    pages: List[Union[str, PageTemplate]]
