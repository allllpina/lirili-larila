from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from config import get_settings
from jose import JWTError, jwt


class Tokenization:
    @staticmethod
    def create_jwt_token(
        user_data: dict, expires_delta: timedelta = timedelta(hours=1)
    ) -> str:
        """
        Generates JWT token using the user information
        """
        __settings = get_settings()

        expire = datetime.now(timezone.utc) + expires_delta
        payload = {"sub": user_data["username"], "user_data": user_data, "exp": expire}

        return jwt.encode(
            payload,
            __settings.secret_key.get_secret_value(),
            algorithm=__settings.algorithm,
        )

    @staticmethod
    def decode_jwt_token(token: str) -> dict | None:
        """
        Decodes JWT token to parse user info
        """
        __settings = get_settings()

        try:
            return jwt.decode(
                token,
                __settings.secret_key.get_secret_value(),
                algorithms=[__settings.algorithm],
            )
        except JWTError:
            return None

    @staticmethod
    def create_refresh_token(length: int = 64) -> str:
        """
        Generates refresh token
        """
        return token_urlsafe(length)

    @staticmethod
    def validate_refresh_token(token: str, stored_token: str) -> bool:
        """
        Checks if stored token is similar to given by frontend
        """
        return token == stored_token
