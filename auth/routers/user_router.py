from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database import User, get_db
from utils.oauth import get_current_user

user_router = APIRouter(tags=["user"])


@user_router.get("/get_current_user")
async def get_current(user_data: User = Depends(get_current_user)):
    fields_to_keep = ["id", "email", "username"]
    user_data = user_data.to_dict(columns=fields_to_keep)
    return user_data


@user_router.get("/get_user_by_id")
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(
        get_current_user
    ),  # `_` - because we don't need that var, but we need to check if user is authorized
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    fields_to_keep = ["id", "email", "username"]
    user = user.to_dict(columns=fields_to_keep)
    return user
