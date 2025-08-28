from datetime import timestamp
from uuid import UUID

from pydantic import BaseModel


class PostBase(BaseModel):
    id: UUID
    username: str
    email: str
    password_hash: str
    token_expires_at: timestamp
    token: str

    class Config:
        orm_mode = True


class CreatePost(PostBase):
    class Config:
        orm_mode = True
