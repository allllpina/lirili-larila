from config import get_settings
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

auth_scheme = HTTPBearer()
settings = get_settings()


def decode_jwt_token(token: str) -> dict:
    """Decodes JWT"""
    try:
        payload = jwt.decode(
            token, settings.jwt_key.get_secret_value(), algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        raise ValueError("Invalid Token")


def get_user_data(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    """
    Function that gets user info from token Bearer in HTTP Authorization header
    """
    try:
        return decode_jwt_token(credentials.credentials)
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired JWT",
            headers={"WWW-Authenticate": "Bearer"},
        )
