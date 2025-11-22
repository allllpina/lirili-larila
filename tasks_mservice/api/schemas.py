from typing import List, Literal, Optional

from db.models import (
    BoardDocument,
    Collaborator,
    CustomField,
    PageDocument,
    ProjectDocument,
    TaskDocument,
)
from pydantic import BaseModel


class TaskCreate(BaseModel):
    name: str
    description: str = ""

    priority: Literal["low", "medium", "high", "None"] = "None"

    status: Literal["complete", "in progress", "not done"] = "not done"

    tags: List[str] = []

    collaborators: List[Collaborator] = []

    custom_fields: List[CustomField] = []


class BoardCreate(BaseModel):
    name: str
    description: str = ""


class PageCreate(BaseModel):
    name: str
    description: str = ""


class ProjectCreate(BaseModel):
    admin_id: int
    name: str
    description: str = ""
    collaborators: List[Collaborator] = []


class FullBoard(BoardDocument):
    tasks: List[TaskDocument] = []


class FullPage(PageDocument):
    boards: List[FullBoard] = []


class FullProject(ProjectDocument):
    pages: List[FullPage] = []


class CollaboratorCostInfo(BaseModel):
    usr_id: int
    hourly_rate: float
    hours_worked: float
    total_pay: float


class TaskPriceInfo(BaseModel):
    task_id: str
    name: str
    total_cost: Optional[float]
    cost_breakdown: List[CollaboratorCostInfo]


class BoardPriceInfo(BaseModel):
    board_id: str
    name: str
    overall: float
    per_task: List[TaskPriceInfo]


class PagePriceInfo(BaseModel):
    page_id: str
    name: str
    overall: float
    per_board: List[BoardPriceInfo]


class ProjectPriceReport(BaseModel):
    project_id: str
    project_name: str
    overall: float
    per_page: List[PagePriceInfo]


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high", "None"]] = None
    status: Optional[Literal["complete", "in progress", "not done"]] = None
    tags: Optional[List[str]] = None
    collaborators: Optional[List[Collaborator]] = None
    custom_fields: Optional[List[CustomField]] = None
    time_to_complete: Optional[float] = None


class BoardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class PageUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    collaborators: Optional[List[Collaborator]] = None


class TaskMoveRequest(BaseModel):
    taskId: str
    boardGiverId: str
    boardReceiverId: str
