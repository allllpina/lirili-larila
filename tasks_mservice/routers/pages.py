from datetime import datetime

from entities_module.entities import Page, Project
from fastapi import APIRouter, Depends, HTTPException, Request
from models.entity_models import PageEdit, PageTemplate
from pymongo.database import Database
from utils.check_access import check_if_accessable, get_user_data
from utils.get_db import get_db

pages_router = APIRouter(tags=["pages", "CRUD"])


@pages_router.post("/create_page", tags=["pages", "create"])
async def create_page(
    page: PageTemplate,
    db: Database = Depends(get_db),
    user_data=Depends(get_user_data),
    request: Request = None,
):
    try:
        # Check, if user have an access to CRUD with this project
        is_accessible = await check_if_accessable(
            user_id=user_data["user_data"]["id"],
            project_id=page.project_id,
            db=db,
        )
        if not is_accessible:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource.",
            )
        # Can be changed to JWT
        data = page.model_dump(by_alias=True)

        date_of_creation = str(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        data["date_of_creation"] = date_of_creation

        project_id = page.project_id
        project = await Project.from_db(project_id, db=db)
        try:
            await project.add_pages(pages=[data], write_to_db=True)

            await request.app.state.SOCKETS.broadcast(
                room=project_id,
                message={"category": "pages", "content": data, "operation": "create"},
            )
            return data
        except RuntimeError as e:
            raise e
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@pages_router.get("/get_page", tags=["pages", "read"])
async def get_page(
    page_id: str,
    project_id: str,
    db: Database = Depends(get_db),
    user_data=Depends(get_user_data),
):
    try:
        # Check, if user have an access to CRUD with this project
        is_accessible = await check_if_accessable(
            user_id=user_data["user_data"]["id"],
            project_id=project_id,
            db=db,
        )
        if not is_accessible:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource.",
            )

        page = await Page.from_db(page_id, db=db)

        return page.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@pages_router.put("/edit_page", tags=["pages", "edit"])
async def edit_page(
    page_template: PageEdit,
    db: Database = Depends(get_db),
    user_data=Depends(get_user_data),
    request: Request = None,
):
    try:
        # Check, if user have an access to CRUD with this project
        is_accessible = await check_if_accessable(
            user_id=user_data["user_data"]["id"],
            project_id=page_template.project_id,
            db=db,
        )
        if not is_accessible:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource.",
            )

        data = page_template.model_dump(exclude_none=True, by_alias=True)
        page_id = data.pop("_id", None)
        project_id = data.pop("project_id")
        page = await Page.from_db(id=page_id, db=db)

        await page.update(**data)
        await request.app.state.SOCKETS.broadcast(
            room=project_id,
            message={"category": "pages", "content": data, "operation": "edit"},
        )

        return page.dump_to_dict()

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))


@pages_router.delete("/delete_page", tags=["pages", "delete"])
async def delete_page(
    page_id: str,
    project_id,
    db: Database = Depends(get_db),
    user_data=Depends(get_user_data),
    request: Request = None,
):
    try:
        # Check, if user have an access to CRUD with this project
        is_accessible = await check_if_accessable(
            user_id=user_data["user_data"]["id"],
            project_id=project_id,
            db=db,
        )
        if not is_accessible:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource.",
            )

        # Make it to depend on Project instance
        page = await Page.from_db(id=page_id, db=db)
        ret = await page.delete_in_db()
        await request.app.state.SOCKETS.broadcast(
            room=page.project_id,
            message={"category": "pages", "content": None, "operation": "delete"},
        )
        return ret
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))
