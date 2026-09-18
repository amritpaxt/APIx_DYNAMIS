from datetime import date, timedelta
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from app.db.models import FareQuote


def last_observed_with_decay(session: Session, route_id: int, window: int, on_date: date, daily_decay: float = .01) -> float | None:
    quote = session.scalar(select(FareQuote).where(FareQuote.route_id == route_id, FareQuote.advance_window == window,
        FareQuote.scrape_ts < on_date).order_by(desc(FareQuote.scrape_ts)))
    if quote is None:
        return None
    elapsed = max(0, (on_date - quote.scrape_ts.date()).days)
    return round((quote.base_fare + quote.taxes) * (1 - daily_decay) ** elapsed, 2)
