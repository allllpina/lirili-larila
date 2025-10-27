from config import get_settings
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.database import Collection

auth_scheme = HTTPBearer()
settings = get_settings()


def get_user_data(
    credentials: HTTPAuthorizationCredentials | str = Depends(auth_scheme),
):
    """
    Function that gets user info from token Bearer in HTTP Authorization header
    """
    if isinstance(credentials, str):
        token = credentials
    else:
        token = credentials.credentials

    try:
        payload = jwt.decode(
            token, settings.jwt_key.get_secret_value(), algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired JWT",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def check_if_accessable(
    user_id: int,
    project_id: str,
    db: AsyncDatabase,
    collection: str = "users",
) -> bool:
    """
    Function that checks if the user in the users collection in db,
    which prevents projects to be available for users which is not allowed to
    """
    collection: Collection = db.get_collection(collection)
    record = await collection.find_one({"_id": project_id})
    return user_id in record["users"]
