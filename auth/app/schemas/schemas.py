from datetime import datetime

from pydantic import (UUID4, BaseModel, EmailStr, field_validator,
                      model_validator)


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: UUID4

    model_config = {"from_attributes": True}

    @field_validator("id", mode="before")
    @classmethod
    def convert_to_str(cls, v):
        return str(v) if v else v


class UserRegister(UserBase):
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def verify_password_match(self):
        if self.password != self.confirm_password:
            raise ValueError("The two passwords did not match.")
        return self


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class JwtTokenSchema(BaseModel):
    token: str
    payload: dict
    expire: datetime


class TokenPair(BaseModel):
    access: JwtTokenSchema
    refresh: JwtTokenSchema


class RefreshToken(BaseModel):
    refresh: str


class SuccessResponseScheme(BaseModel):
    msg: str


class BlackListToken(BaseModel):
    id: UUID4
    expire: datetime

    model_config = {"from_attributes": True}


class MailBodySchema(BaseModel):
    token: str
    type: str


class EmailSchema(BaseModel):
    recipients: list[EmailStr]
    subject: str
    body: MailBodySchema


class MailTaskSchema(BaseModel):
    user: User
    body: MailBodySchema


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class PasswordResetSchema(BaseModel):
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def verify_password_match(self):
        if self.password != self.confirm_password:
            raise ValueError("The two passwords did not match.")
        return self


class PasswordUpdateSchema(PasswordResetSchema):
    old_password: str


class OldPasswordErrorSchema(BaseModel):
    old_password: bool

    @field_validator("old_password")
    @classmethod
    def check_old_password_status(cls, v):
        if not v:
            raise ValueError("Old password is not correct")
        return v
