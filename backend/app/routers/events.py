"""Events endpoints: retrieve security events with role-based access."""

from sqlmodel import Session, select
from fastapi import APIRouter, Depends

from ..schemas import EventOut
from ..models import User, Event
from ..database import get_session
from ..deps import get_current_user
from ..errors import NotFoundError

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=list[EventOut])
async def get_events(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[EventOut]:
    """Get all security events (role-based visibility).

    All authenticated active users see all events. Events returned are filtered through
    EventOut schema which applies HTML escaping to title/description for XSS safety.

    Returns array of events (200).
    """
    # Role-based visibility: all active users see all events
    stmt = select(Event)
    events = session.exec(stmt).all()
    return [EventOut(**event.dict()) for event in events]


@router.get("/{event_id}", response_model=EventOut)
async def get_event(
    event_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> EventOut:
    """Get a single security event by ID.

    All authenticated active users can access any event (role-based visibility).

    Returns the event (200) or {error: "..."} (404).
    """
    event = session.get(Event, event_id)
    if not event:
        raise NotFoundError("Event not found")
    return EventOut(**event.dict())
