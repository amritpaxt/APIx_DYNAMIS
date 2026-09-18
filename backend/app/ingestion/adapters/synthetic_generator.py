from __future__ import annotations
from datetime import date, datetime, time, timedelta, timezone
from math import sin
from random import Random
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import Carrier, FareQuote, Route, Source

ROUTE_BASKET = [("DEL", "BOM", .18), ("DEL", "BLR", .14), ("BOM", "BLR", .13), ("DEL", "CCU", .09),
                ("BLR", "HYD", .08), ("MAA", "DEL", .08), ("DEL", "PNQ", .07), ("BOM", "GOI", .06),
                ("DEL", "HYD", .09), ("CCU", "BLR", .08)]
CARRIERS = [("IndiGo", "6E"), ("Air India", "AI"), ("Akasa Air", "QP"), ("SpiceJet", "SG")]
SOURCES = [("IndiGo", "airline"), ("Air India", "airline"), ("Air India Express", "airline"), ("Akasa Air", "airline"),
           ("SpiceJet", "airline"), ("MakeMyTrip", "ota"), ("Yatra", "ota"), ("EaseMyTrip", "ota"),
           ("Cleartrip", "ota"), ("Ixigo", "ota"), ("Goibibo", "ota")]
WINDOWS = (1, 7, 15, 30, 45)


def ensure_reference_data(session: Session) -> None:
    if not session.scalar(select(Route.id).limit(1)):
        session.add_all(Route(origin=a, destination=b, dgca_traffic_weight=w) for a, b, w in ROUTE_BASKET)
    if not session.scalar(select(Carrier.id).limit(1)):
        session.add_all(Carrier(name=name, iata_code=code) for name, code in CARRIERS)
    if not session.scalar(select(Source.id).limit(1)):
        session.add_all(Source(name=name, type=kind, robots_txt_status="synthetic") for name, kind in SOURCES)
    session.commit()


def seed_quotes(session: Session, days: int = 60, seed: int = 26056) -> int:
    """Create reproducible, seasonal and imperfect demo data without pretending it is live data."""
    ensure_reference_data(session)
    if session.scalar(select(FareQuote.id).limit(1)):
        return 0
    rng = Random(seed)
    routes, carriers, sources = list(session.scalars(select(Route))), list(session.scalars(select(Carrier))), list(session.scalars(select(Source)))
    start = date.today() - timedelta(days=days)
    records: list[FareQuote] = []
    for day_offset in range(days):
        quote_day = start + timedelta(days=day_offset)
        season = 1 + .07 * sin(day_offset / 6) + (.13 if quote_day.weekday() in (4, 5) else 0)
        for route in routes:
            route_factor = 0.82 + route.id * .075
            for window in WINDOWS:
                lead_factor = 1 + (45 - window) * .012
                for carrier in carriers:
                    # One or two providers per observation gives realistic source coverage variation.
                    for source in rng.sample(sources, k=2):
                        status_roll = rng.random()
                        status = "sold_out" if status_roll < .012 else "cancelled" if status_roll < .018 else "operating"
                        base = 3900 * route_factor * lead_factor * season * (1 + rng.gauss(0, .045))
                        if rng.random() < .006:  # rare genuine demand spike, later flagged transparently
                            base *= 1.75
                        tax = max(420, round(base * .12, 2))
                        fee = round(rng.uniform(0, 420) if source.type == "ota" else 0, 2)
                        ts = datetime.combine(quote_day, time(9 + (source.id % 3) * 5), tzinfo=timezone.utc)
                        records.append(FareQuote(route_id=route.id, carrier_id=carrier.id, source_id=source.id,
                            fare_class="economy", advance_window=window, departure_date=quote_day + timedelta(days=window),
                            scrape_ts=ts, flight_no=f"{carrier.iata_code}{100 + route.id}", base_fare=round(base, 2), taxes=round(tax, 2),
                            convenience_fee=fee, total_fare=round(base + tax + fee, 2), seats_available=rng.randint(2, 32) if status == "operating" else 0,
                            flight_status=status, raw_payload={"fixture": "synthetic", "source": source.name, "seed": seed}))
    session.add_all(records)
    session.commit()
    return len(records)
