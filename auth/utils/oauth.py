from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import User, get_db
from .jwt import Tokenization as Tkn

auth_scheme = HTTPBearer()


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = Tkn.decode_jwt_token(token.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_data = payload.get("user_data")
    if not user_data:
        raise HTTPException(status_code=401, detail="No user data in token")

    user_id = user_data.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="No user id in token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
