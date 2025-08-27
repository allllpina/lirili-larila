from entities_module.entities import Project
from fastapi import APIRouter, Depends, HTTPException
from models.entity_models import ProjectEdit, ProjectTemplate
from pymongo.database import Database
from utils.get_db import get_db

projects_router = APIRouter(tags=["projects", "CRUD"])


@projects_router.post("/create_project", tags=["projects", "create"])
async def create_project(project: ProjectTemplate, db: Database = Depends(get_db)):
    try:
        # Can be changed to JWT
        data = project.model_dump(by_alias=True)
        _ = data.pop("user_id")

        project: Project = await Project.from_template(template=data, db=db)
        try:
            await project.write_to_db()
            return project.dump_to_dict()
        except RuntimeError as e:
            raise e
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@projects_router.get("/get_project", tags=["projects", "read"])
async def get_project(user_id: int, project_id: str, db: Database = Depends(get_db)):
    try:
        project = await Project.from_db(project_id, db=db)

        return project.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@projects_router.put("/edit_project", tags=["projects", "edit"])
async def edit_project(project_template: ProjectEdit, db: Database = Depends(get_db)):
    try:
        data = project_template.model_dump(exclude_none=True, by_alias=True)
        _ = data.pop("user_id", None)
        project_id = data.pop("_id", None)
        project = await Project.from_db(id=project_id, db=db)

        await project.update(**data)

        return project.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))
