from datetime import datetime

from entities_module.entities import Page, Project
from fastapi import APIRouter, Depends, HTTPException
from models.entity_models import PageEdit, PageTemplate
from pymongo.database import Database
from utils.get_db import get_db

pages_router = APIRouter(tags=["pages", "CRUD"])


@pages_router.post("/create_page", tags=["pages", "create"])
async def create_page(page: PageTemplate, db: Database = Depends(get_db)):
    try:
        # Can be changed to JWT
        data = page.model_dump(by_alias=True)

        date_of_creation = str(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        data["date_of_creation"] = date_of_creation

        project_id = page.project_id
        _ = data.pop("user_id")
        project = await Project.from_db(project_id, db=db)
        try:
            await project.add_pages(pages=[data], write_to_db=True)

            return data
        except RuntimeError as e:
            raise e
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@pages_router.get("/get_page", tags=["pages", "read"])
async def get_page(user_id: int, page_id: str, db: Database = Depends(get_db)):
    try:
        page = await Page.from_db(page_id, db=db)

        return page.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@pages_router.put("/edit_page", tags=["pages", "edit"])
async def edit_page(page_template: PageEdit, db: Database = Depends(get_db)):
    try:
        data = page_template.model_dump(exclude_none=True, by_alias=True)
        _ = data.pop("user_id", None)
        page_id = data.pop("_id", None)
        page = await Page.from_db(id=page_id, db=db)

        await page.update(**data)

        return page.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@pages_router.delete("/delete_page", tags=["pages", "delete"])
async def delete_page(page_id: str, db: Database = Depends(get_db)):
    try:
        # Make it to depend on Project instance
        page = await Page.from_db(id=page_id, db=db)
        ret = await page.delete_in_db()
        return ret
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))
