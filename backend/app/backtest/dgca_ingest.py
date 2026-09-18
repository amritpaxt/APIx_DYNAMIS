"""Ingest an authorised DGCA/MoSPI CSV export into the reference-fare table.

The eSankhyiki portal offers CSV downloads. This adapter intentionally consumes an
operator-supplied export rather than probing private endpoints or bypassing portal controls.
Expected columns: origin, destination, month, avg_fare, passenger_count (optional).
"""
from __future__ import annotations
import csv
from datetime import date, datetime
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import DGCAMonthlyAvg, Route


def _month(value: str) -> date:
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m", "%d-%m-%Y"):
        try:
            parsed = datetime.strptime(value, fmt).date()
            return parsed.replace(day=1)
        except ValueError:
            continue
    raise ValueError(f"Unsupported month value: {value!r}")


def ingest_csv(session: Session, path: str | Path) -> int:
    route_ids = {(route.origin.upper(), route.destination.upper()): route.id for route in session.scalars(select(Route))}
    imported = 0
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row["origin"].strip().upper(), row["destination"].strip().upper())
            if key not in route_ids:
                continue
            month = _month(row["month"])
            existing = session.scalar(select(DGCAMonthlyAvg).where(DGCAMonthlyAvg.route_id == route_ids[key], DGCAMonthlyAvg.month == month))
            values = {"avg_fare": float(row["avg_fare"]), "passenger_count": int(row["passenger_count"]) if row.get("passenger_count") else None}
            if existing:
                existing.avg_fare, existing.passenger_count = values["avg_fare"], values["passenger_count"]
            else:
                session.add(DGCAMonthlyAvg(route_id=route_ids[key], month=month, **values))
            imported += 1
    session.commit()
    return imported
