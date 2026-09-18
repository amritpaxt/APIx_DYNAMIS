from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import FareQuote, Route
from app.db.session import get_db
from app.pipeline.cleaning import index_eligible

router = APIRouter(prefix="/elasticity", tags=["elasticity"])


@router.get("/{route_id}")
def elasticity(route_id: int, db: Session = Depends(get_db)) -> dict:
    route = db.get(Route, route_id)
    if not route:
        raise HTTPException(404, "Unknown route")
    buckets: dict[int, list[float]] = defaultdict(list)
    for quote in db.scalars(select(FareQuote).where(FareQuote.route_id == route_id)):
        if index_eligible(quote):
            buckets[quote.advance_window].append(quote.base_fare + quote.taxes)
    points = [{"advance_window": window, "average_fare": round(sum(fares) / len(fares), 2)} for window, fares in sorted(buckets.items())]
    return {"route_id": route_id, "route": f"{route.origin}-{route.destination}", "points": points}
