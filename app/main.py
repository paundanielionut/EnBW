import logging
from typing import List, Dict
from fastapi import FastAPI, HTTPException, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid

from database import AsyncSessionLocal, engine
from models import Base, Event
from pydantic import BaseModel


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


logger = logging.getLogger(__name__)

app = FastAPI()

EVENT_BUCKET_PATTERN = r'^[a-zA-Z0-9_.-]+$'

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
    logger.info("Starting up the application and creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully.")


@app.put("/v1/{event_bucket}/", response_model=Dict[str, str])
async def create_event(
        event: EventCreate,
        event_bucket: str = Path(
            ...,
            title="The batch id, restricted to certain characters",
            pattern=EVENT_BUCKET_PATTERN
        ),
        db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    event_id = str(uuid.uuid4())  # Generate a unique ID for the event
    new_event = Event(
        bucket_id=event_bucket,
        event_id=event_id,
        title=event.title,
        message=event.message,
    )
    db.add(new_event)
    await db.commit()
    logger.info(f"Event created with ID: {event_id} in bucket: {event_bucket}")
    return {"event_id": event_id}


@app.get("/v1/{event_bucket}/", response_model=Dict[str, List[str]])
async def list_event_ids(
        event_bucket: str = Path(
            ...,
            title="The batch id, restricted to certain characters",
            pattern=EVENT_BUCKET_PATTERN
        ),
        db: AsyncSession = Depends(get_db)
) -> Dict[str, List[str]]:
    logger.info(f"Fetching event IDs from bucket: {event_bucket}")
    result = await db.execute(select(Event.event_id).filter(Event.bucket_id == event_bucket))
    event_ids = [row for row in result.scalars().all()]
    if not event_ids:
        logger.warning(f"No events found in bucket: {event_bucket}")
        raise HTTPException(status_code=404, detail="No events found in this bucket")
    logger.info(f"Found {len(event_ids)} event(s) in bucket: {event_bucket}")
    return {"event_ids": event_ids}


@app.get("/v1/{event_bucket}/{event_id}", response_model=Dict[str, str])
async def get_event(
        event_id: str,
        event_bucket: str = Path(
            ...,
            title="The batch id, restricted to certain characters",
            pattern=EVENT_BUCKET_PATTERN
        ),
        db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    logger.info(f"Fetching event with ID: {event_id} from bucket: {event_bucket}")
    result = await db.execute(
        select(Event).filter(Event.bucket_id == event_bucket, Event.event_id == event_id)
    )
    event = result.scalars().first()
    if event is None:
        logger.error(f"Event with ID: {event_id} not found in bucket: {event_bucket}")
        raise HTTPException(status_code=404, detail="Event not found")
    logger.info(f"Event with ID: {event_id} retrieved successfully from bucket: {event_bucket}")
    return {
        "ID": event.event_id,
        "title": event.title,
        "message": event.message
    }
