from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"

    event_id = Column(String, primary_key=True, index=True, unique=True)
    bucket_id = Column(String, index=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
