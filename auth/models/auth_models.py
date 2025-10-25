from typing import Annotated, Union

from pydantic import BaseModel, EmailStr, StringConstraints

# Створюємо "тип із обмеженнями"
UsernameStr = Annotated[str, StringConstraints(min_length=3, max_length=50)]
PasswordStr = Annotated[str, StringConstraints(min_length=6, max_length=128)]


class UserRegister(BaseModel):
    email: EmailStr
    username: UsernameStr
    password: PasswordStr


class UserLogin(BaseModel):
    login: Union[EmailStr, UsernameStr]
    password: PasswordStr
