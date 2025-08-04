from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from uuid import uuid4
from app.db.base import Base

class Entry(Base):
    __tablename__ = "entry"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    work = Column(String(256), nullable=False)
    struggle = Column(String(256), nullable=False)
    intention = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
