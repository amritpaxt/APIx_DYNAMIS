from __future__ import annotations
from collections import defaultdict
from datetime import timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import FareQuote
from app.pipeline.outliers import mad_flags

CANONICAL_STATUSES = {"operating", "cancelled", "sold_out"}


def normalize_record(raw: dict) -> dict:
    """Normalize a raw adapter response without discarding audit fields or channel fees."""
    status = str(raw.get("flight_status", "operating")).lower()
    status = status if status in CANONICAL_STATUSES else "operating"
    base = round(float(raw["base_fare"]), 2)
    taxes = round(float(raw.get("taxes", 0)), 2)
    fee = round(float(raw.get("convenience_fee", 0)), 2)
    return {**raw, "base_fare": base, "taxes": taxes, "convenience_fee": fee,
            "total_fare": round(float(raw.get("total_fare", base + taxes + fee)), 2), "flight_status": status}


def deduplicate_quotes(quotes: list[FareQuote], bucket_minutes: int = 30) -> list[FareQuote]:
    seen: set[tuple] = set()
    kept: list[FareQuote] = []
    for quote in sorted(quotes, key=lambda item: item.scrape_ts):
        bucket = quote.scrape_ts - timedelta(minutes=quote.scrape_ts.minute % bucket_minutes,
                                               seconds=quote.scrape_ts.second, microseconds=quote.scrape_ts.microsecond)
        key = (quote.route_id, quote.departure_date, quote.advance_window, quote.carrier_id, quote.flight_no, quote.fare_class, bucket)
        if key not in seen:
            seen.add(key)
            kept.append(quote)
    return kept


def flag_outliers(session: Session) -> int:
    quotes = list(session.scalars(select(FareQuote).where(FareQuote.fare_class == "economy")))
    cohorts: dict[tuple, list[FareQuote]] = defaultdict(list)
    for quote in quotes:
        cohorts[(quote.route_id, quote.advance_window, quote.scrape_ts.date())].append(quote)
    changed = 0
    for cohort in cohorts.values():
        for quote, flagged in zip(cohort, mad_flags([q.base_fare + q.taxes for q in cohort])):
            if quote.is_outlier != flagged:
                quote.is_outlier = flagged
                changed += 1
    session.commit()
    return changed


def index_eligible(quote: FareQuote) -> bool:
    # Convenience fees remain in storage but are excluded from the inflation measure.
    return quote.fare_class == "economy" and quote.flight_status == "operating" and not quote.is_outlier
