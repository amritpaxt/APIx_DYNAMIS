from collections import Counter
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import FareQuote, Route


def traffic_weights(session: Session) -> dict[int, float]:
    routes = list(session.scalars(select(Route).where(Route.active.is_(True))))
    total = sum(route.dgca_traffic_weight for route in routes)
    return {route.id: route.dgca_traffic_weight / total for route in routes} if total else {}


def booking_window_weights(quotes: list[FareQuote]) -> dict[int, float]:
    counts = Counter(q.advance_window for q in quotes if q.fare_class == "economy")
    total = sum(counts.values())
    return {window: count / total for window, count in counts.items()} if total else {}
