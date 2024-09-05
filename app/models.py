from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"

    event_id = Column(String, primary_key=True, index=True, unique=True)  # UUID as the primary key
    bucket_id = Column(String, index=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
