import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 30
REFRESH_TOKEN_EXPIRES_MINUTES = 15 * 24 * 60  # 15 days

DATABASE_URL = os.getenv("DATABASE_URL")
