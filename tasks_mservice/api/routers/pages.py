from api.dependencies import get_page_service
from api.schemas import PageCreate, PageDocument, PageUpdate
from fastapi import APIRouter, Depends, HTTPException, Request
from services.exceptions import NotFoundError, PermissionDeniedError
from services.page_service import PageService
from utils.check_access import get_user_data

router = APIRouter(prefix="/pages", tags=["Pages"])


@router.post("/create_page", response_model=PageDocument)
async def create_page(
    page: PageCreate,
    project_id: str,
    request: Request,
    user_data: dict = Depends(get_user_data),
    service: PageService = Depends(get_page_service),
):
    try:
        user_id = user_data["user_data"]["id"]
        new_page = await service.create_page(page, project_id, user_id)

        await request.app.state.SOCKETS.broadcast(
            room=project_id,
            message={
                "category": "pages",
                "content": new_page.model_dump(),
                "operation": "create",
            },
        )

        return new_page

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/delete_page/{page_id}")
async def delete_page(
    page_id: str,
    request: Request,
    user_data: dict = Depends(get_user_data),
    service: PageService = Depends(get_page_service),
):
    try:
        user_id = user_data["user_data"]["id"]
        page_doc = await service.get_page(page_id, user_id)
        project_id = page_doc.project_id

        result = await service.delete_page(page_id, user_id)

        await request.app.state.SOCKETS.broadcast(
            room=project_id,
            message={
                "category": "pages",
                "content": {"id": page_id},
                "operation": "delete",
            },
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get_page/{page_id}", response_model=PageDocument)
async def get_page(
    page_id: str,
    user_data: dict = Depends(get_user_data),
    service: PageService = Depends(get_page_service),
):
    try:
        user_id = user_data["user_data"]["id"]
        return await service.get_page(page_id, user_id)
    except (NotFoundError, PermissionDeniedError) as e:
        raise HTTPException(
            status_code=404 if isinstance(e, NotFoundError) else 403, detail=str(e)
        )


@router.put("/edit_page", response_model=PageDocument)
async def edit_page(
    page: PageUpdate,
    page_id: str,
    request: Request,
    user_data: dict = Depends(get_user_data),
    service: PageService = Depends(get_page_service),
):
    try:
        user_id = user_data["user_data"]["id"]
        page_doc = await service.get_page(page_id, user_id)
        project_id = page_doc.project_id

        result = await service.update_page(page_id, page, user_id)

        await request.app.state.SOCKETS.broadcast(
            room=project_id,
            message={
                "category": "pages",
                "content": result.model_dump(),
                "operation": "edit",
            },
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
