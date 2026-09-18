from collections import defaultdict
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import FareQuote, Route
from app.db.session import get_db
from app.pipeline.cleaning import index_eligible

router = APIRouter(prefix="/heatmap", tags=["heatmap"])


@router.get("")
def heatmap(day: date | None = None, db: Session = Depends(get_db)) -> dict:
    quotes = list(db.scalars(select(FareQuote)))
    if not quotes:
        return {"date": day, "cells": []}
    target = day or max(q.scrape_ts.date() for q in quotes)
    grouped: dict[tuple[int, int], list[float]] = defaultdict(list)
    for quote in quotes:
        if quote.scrape_ts.date() == target and index_eligible(quote):
            grouped[(quote.route_id, quote.advance_window)].append(quote.base_fare + quote.taxes)
    names = {route.id: f"{route.origin}-{route.destination}" for route in db.scalars(select(Route))}
    return {"date": target, "cells": [{"route_id": rid, "route": names[rid], "window": window, "fare": round(sum(values) / len(values), 2)}
                                      for (rid, window), values in sorted(grouped.items())]}
