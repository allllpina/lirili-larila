from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import User, get_db
from .jwt import Tokenization as Tkn

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    payload = Tkn.decode_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_data = payload.get("sub")
    if not user_data:
        raise HTTPException(status_code=401, detail="No user data in token")

    user_id = user_data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="No user id in token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
