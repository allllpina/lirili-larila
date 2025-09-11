from datetime import datetime
from typing import Annotated

from app.core.dependencies import get_db
from app.core.exceptions import (BadRequestException, ForbiddenException,
                                 NotFoundException)
from app.core.hash import get_password_hash, verify_password
from app.core.jwt import (EXP, JTI, SUB, add_refresh_token_cookie,
                          create_token_pair, decode_access_token, mail_token,
                          refresh_token_state)
from app.models import models
from app.schemas import schemas
from app.utils.mail import user_mail_event
from fastapi import (APIRouter, BackgroundTasks, Cookie, Depends,
                     HTTPException, Response)
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post("/register", response_model=schemas.User)
async def register(
    data: schemas.UserRegister,
    bg_task: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    user = await models.User.find_by_email(db=db, email=data.email)
    if user:
        raise HTTPException(status_code=400, detail="Email has already registered")

    # hashing password
    user_data = data.dict(exclude={"confirm_password"})
    user_data["password"] = get_password_hash(user_data["password"])

    # save user to db
    user = models.User(**user_data)
    user.is_active = False
    await user.save(db=db)

    # send verify email
    user_schema = schemas.User.from_orm(user)
    verify_token = mail_token(user_schema)

    mail_task_data = schemas.MailTaskSchema(
        user=user_schema, body=schemas.MailBodySchema(type="verify", token=verify_token)
    )
    bg_task.add_task(user_mail_event, mail_task_data)

    return user_schema


@router.post("/login")
async def login(
    data: schemas.UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user = await models.User.authenticate(
        db=db, email=data.email, password=data.password
    )

    if not user:
        raise BadRequestException(detail="Incorrect email or password")

    if not user.is_active:
        raise ForbiddenException()

    user = schemas.User.from_orm(user)

    token_pair = create_token_pair(user=user)

    add_refresh_token_cookie(response=response, token=token_pair.refresh.token)

    return {"token": token_pair.access.token}


@router.post("/refresh")
async def refresh(refresh: Annotated[str | None, Cookie()] = None):
    print(refresh)
    if not refresh:
        raise BadRequestException(detail="refresh token required")
    return refresh_token_state(token=refresh)


@router.get("/verify", response_model=schemas.SuccessResponseScheme)
async def verify(token: str, db: AsyncSession = Depends(get_db)):
    payload = await decode_access_token(token=token, db=db)
    user = await models.User.find_by_id(db=db, id=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")

    user.is_active = True
    await user.save(db=db)
    return {"msg": "Successfully activated"}


@router.post("/logout", response_model=schemas.SuccessResponseScheme)
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
):
    payload = await decode_access_token(token=token, db=db)
    black_listed = models.BlackListToken(
        id=payload[JTI], expire=datetime.utcfromtimestamp(payload[EXP])
    )
    await black_listed.save(db=db)

    return {"msg": "Succesfully logout"}


@router.post("/forgot-password", response_model=schemas.SuccessResponseScheme)
async def forgot_password(
    data: schemas.ForgotPasswordSchema,
    bg_task: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    user = await models.User.find_by_email(db=db, email=data.email)
    if user:
        user_schema = schemas.User.from_orm(user)
        reset_token = mail_token(user_schema)

        mail_task_data = schemas.MailTaskSchema(
            user=user_schema,
            body=schemas.MailBodySchema(type="password-reset", token=reset_token),
        )
        bg_task.add_task(user_mail_event, mail_task_data)

    return {"msg": "Reset token sended successfully your email check your email"}


@router.post("/password-reset", response_model=schemas.SuccessResponseScheme)
async def password_reset_token(
    token: str,
    data: schemas.PasswordResetSchema,
    db: AsyncSession = Depends(get_db),
):
    payload = await decode_access_token(token=token, db=db)
    user = await models.User.find_by_id(db=db, id=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")

    user.password = get_password_hash(data.password)
    await user.save(db=db)

    return {"msg": "Password succesfully updated"}


@router.post("/password-update", response_model=schemas.SuccessResponseScheme)
async def password_update(
    token: Annotated[str, Depends(oauth2_scheme)],
    data: schemas.PasswordUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    payload = await decode_access_token(token=token, db=db)
    user = await models.User.find_by_id(db=db, id=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")

    # raise Validation error
    if not verify_password(data.old_password, user.password):
        try:
            schemas.OldPasswordErrorSchema(old_password=False)
        except ValidationError as e:
            raise RequestValidationError(e.raw_errors)
    user.password = get_password_hash(data.password)
    await user.save(db=db)

    return {"msg": "Successfully updated"}
