import uuid

from sqlalchemy import TIMESTAMP, UUID, Boolean, Column, String, Varchar, text
from src.db.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(Varchar(255))
    email = Column(String)
    password_hash = Column(Boolean)
    token_expires_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
