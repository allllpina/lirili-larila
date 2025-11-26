from db.database import get_database
from db.repositories import (
    BoardRepository,
    PageRepository,
    ProjectRepository,
    TaskRepository,
    UsersRepository,
)
from fastapi import Depends
from pymongo.asynchronous.database import AsyncDatabase
from services.board_service import BoardService
from services.page_service import PageService
from services.project_service import ProjectService
from services.task_service import TaskService

# --- ЗБИРАЄМО РЕПОЗИТОРІЇ ---
# FastAPI автоматично викличе get_database() і передасть 'db' сюди


def get_task_repo(db: AsyncDatabase = Depends(get_database)) -> TaskRepository:
    return TaskRepository(db)


def get_board_repo(db: AsyncDatabase = Depends(get_database)) -> BoardRepository:
    return BoardRepository(db)


def get_page_repo(db: AsyncDatabase = Depends(get_database)) -> PageRepository:
    return PageRepository(db)


def get_project_repo(db: AsyncDatabase = Depends(get_database)) -> ProjectRepository:
    return ProjectRepository(db)


def get_users_repo(db: AsyncDatabase = Depends(get_database)) -> UsersRepository:
    return UsersRepository(db)


# --- ЗБИРАЄМО СЕРВІСИ (Ієрархічно) ---


def get_task_service(
    task_repo: TaskRepository = Depends(get_task_repo),
    users_repo: UsersRepository = Depends(get_users_repo),
    db: AsyncDatabase = Depends(get_database),
) -> TaskService:
    return TaskService(task_repo=task_repo, db=db, users_repo=users_repo)


def get_board_service(
    task_repo: TaskRepository = Depends(get_task_repo),
    board_repo: BoardRepository = Depends(get_board_repo),
    page_repo: PageRepository = Depends(get_page_repo),
    users_repo: UsersRepository = Depends(get_users_repo),
    task_service: TaskService = Depends(get_task_service),
    db: AsyncDatabase = Depends(get_database),
) -> BoardService:
    return BoardService(
        task_repo=task_repo,
        board_repo=board_repo,
        page_repo=page_repo,
        task_service=task_service,
        db=db,
        users_repo=users_repo,
    )


def get_page_service(
    page_repo: PageRepository = Depends(get_page_repo),
    project_repo: ProjectRepository = Depends(get_project_repo),
    users_repo: UsersRepository = Depends(get_users_repo),
    board_service: BoardService = Depends(get_board_service),
    db: AsyncDatabase = Depends(get_database),
) -> PageService:
    return PageService(
        page_repo=page_repo,
        project_repo=project_repo,
        board_service=board_service,
        users_repo=users_repo,
        db=db,
    )


def get_project_service(
    project_repo: ProjectRepository = Depends(get_project_repo),
    page_repo: PageRepository = Depends(get_page_repo),
    board_repo: BoardRepository = Depends(get_board_repo),
    task_repo: TaskRepository = Depends(get_task_repo),
    users_repo: UsersRepository = Depends(get_users_repo),
    page_service: PageService = Depends(get_page_service),
    db: AsyncDatabase = Depends(get_database),
) -> ProjectService:
    return ProjectService(
        project_repo=project_repo,
        page_repo=page_repo,
        board_repo=board_repo,
        task_repo=task_repo,
        db=db,
        page_service=page_service,
        users_repo=users_repo,
    )
