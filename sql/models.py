from sqlalchemy import Column, String, DateTime

from .database import Base


class Inbox(Base):
    __tablename__ = "inbox"

    code = Column(String, nullable=False)
    name = Column(String, primary_key=True, nullable=False)
    date = Column(DateTime, nullable=False)
