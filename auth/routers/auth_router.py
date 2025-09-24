from authlib.integrations.starlette_client import OAuth
from config import get_settings
from fastapi import APIRouter, Depends, HTTPException, Request
from models.auth_models import UserLogin, UserRegister
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database import User, get_db
from utils.jwt import Tokenization as Tkn
from utils.pwd_crypt import hash_password, verify_password

settings = get_settings()

auth_router = APIRouter(prefix="/auth", tags=["auth"])

oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.google_client_id.get_secret_value(),
    client_secret=settings.google_client_secret.get_secret_value(),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@auth_router.post("/register")
async def register(user: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail="User with this email already exists"
        )
    password_hash = hash_password(user.password)

    userObj = User(
        username=user.username,
        email=user.email,
        password_hash=password_hash,
        refresh_token=Tkn.create_refresh_token(),
    )

    db.add(userObj)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    await db.refresh(userObj)

    user_data = {"id": userObj.id, "username": user.username}
    return Tkn.create_jwt_token(user_data=user_data)


@auth_router.post("/token")
async def token(creds: UserLogin, db: AsyncSession = Depends(get_db)):
    if "@" in creds.login:
        result = await db.execute(select(User).where(User.email == creds.login))
    else:
        result = await db.execute(select(User).where(User.username == creds.login))

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(creds.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_data = {"id": user.id, "username": user.username}
    return Tkn.create_jwt_token(user_data=user_data)


@auth_router.get("/google/login")
async def login_google(request: Request):
    redirect_uri = request.url_for("auth_google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@auth_router.get("/google/callback")
async def auth_google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.userinfo(token=token)
    email = user_info["email"]

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            username=user_info["name"],
            email=email,
            is_oauth_user=True,
            refresh_token=Tkn.create_refresh_token(),
            oauth_provider="google",
            oauth_sub=user_info["sub"],
        )

        db.add(user)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise
        await db.refresh(user)

    user_data = {"id": user.id, "username": user.username}

    return Tkn.create_jwt_token(user_data=user_data)
