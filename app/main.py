from typing import List, Dict
from fastapi import FastAPI, HTTPException, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
import re

from database import AsyncSessionLocal, engine
from models import Base, Event
from pydantic import BaseModel

app = FastAPI()


class EventCreate(BaseModel):
    """
    Pydantic model for event creation
    """
    title: str
    message: str


async def get_db() -> AsyncSession:
    """
    Dependency for getting an async session
    :return: session
    """
    async with AsyncSessionLocal() as session:
        yield session

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def validate_batch_id(batch_id: str) -> None:
    """
    Helper function to validate batch_id
    :param batch_id:
    :return:
    """
    rule = r'^[a-zA-Z0-9_.-]+$'
    if not re.match(rule, batch_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid batch ID. Allowed characters are a-z, A-Z, 0-9, '-', '_', and '.'"
        )

@app.put("/v1/{event_bucket}/", response_model=Dict[str, str])
async def create_event(
        event: EventCreate,
        event_bucket: str = Path(
            ...,
            title="The batch id, restricted to certain characters",
            regex=r'^[a-zA-Z0-9_.-]+$'
        ),
        db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    validate_batch_id(event_bucket)
    event_id = str(uuid.uuid4())  # Generate a unique ID for the event
    new_event = Event(
        bucket_id=event_bucket,
        event_id=event_id,
        title=event.title,
        message=event.message,
    )
    db.add(new_event)
    await db.commit()
    return {"event_id": event_id}


@app.get("/v1/{event_bucket}/", response_model=Dict[str, List[str]])
async def list_event_ids(
        event_bucket: str = Path(
            ...,
            title="The batch id, restricted to certain characters",
            regex=r'^[a-zA-Z0-9_.-]+$'
        ),
        db: AsyncSession = Depends(get_db)
) -> Dict[str, List[str]]:
    result = await db.execute(select(Event.event_id).filter(Event.bucket_id == event_bucket))
    event_ids = [row[0] for row in result.fetchall()]
    if not event_ids:
        raise HTTPException(status_code=404, detail="No events found in this bucket")
    return {"event_ids": event_ids}


@app.get("/v1/{event_bucket}/{event_id}", response_model=Dict[str, str])
async def get_event(
        event_id: str,
        event_bucket: str = Path(
            ...,
            title="The batch id, restricted to certain characters",
            regex=r'^[a-zA-Z0-9_.-]+$'
        ),
        db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    result = await db.execute(
        select(Event).filter(Event.bucket_id == event_bucket, Event.event_id == event_id)
    )
    event = result.scalars().first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return {
        "ID": event.event_id,
        "title": event.title,
        "message": event.message
    }
