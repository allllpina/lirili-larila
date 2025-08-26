import uuid

from sqlalchemy import TIMESTAMP, UUID, Boolean, Column, Integer, String, text
from src.db.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String)
    content = Column(String)
    published = Column(Boolean)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
