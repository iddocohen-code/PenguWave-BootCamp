"""Triage endpoint: AI SOC-analyst assessment of a single security event."""

from sqlmodel import Session
from fastapi import APIRouter, Depends

from ..ai import triage_event
from ..schemas import TriageOut
from ..models import User, Event
from ..database import get_session
from ..deps import get_current_user
from ..errors import NotFoundError

router = APIRouter(prefix="/api/events", tags=["triage"])


@router.post("/{event_id}/triage", response_model=TriageOut)
async def triage(
    event_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TriageOut:
    """Generate an AI triage (SUMMARY / BLAST RADIUS / NEXT STEP) for an event.

    Any authenticated active user can request triage, consistent with event visibility.
    Returns the triage (200), {error: "..."} (404) if the event is unknown, or 502/503
    if the AI backend is unavailable.
    """
    event = session.get(Event, event_id)
    if not event:
        raise NotFoundError("Event not found")

    result = await triage_event(event)
    return TriageOut(event_id=event.id, severity=event.severity, **result)
