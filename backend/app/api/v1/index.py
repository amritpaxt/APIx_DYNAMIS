from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import IndexValue
from app.db.session import get_db

router = APIRouter(prefix="/index", tags=["index"])


def serialize(item: IndexValue) -> dict:
    return {"date": item.date, "frequency": item.frequency, "route_id": item.route_id, "value": item.value,
            "spread_sub_index": item.spread_sub_index, "confidence_score": item.confidence_score,
            "coverage_pct": item.coverage_pct, "outlier_rate": item.outlier_rate, "chain_break": item.chain_break}


@router.get("")
def get_index(frequency: str = Query("daily", alias="freq", pattern="^(daily|weekly|monthly)$"),
              date_from: date | None = Query(None, alias="from"), date_to: date | None = Query(None, alias="to"), db: Session = Depends(get_db)) -> list[dict]:
    query = select(IndexValue).where(IndexValue.frequency == frequency, IndexValue.route_id.is_(None)).order_by(IndexValue.date)
    if date_from:
        query = query.where(IndexValue.date >= date_from)
    if date_to:
        query = query.where(IndexValue.date <= date_to)
    return [serialize(row) for row in db.scalars(query)]


@router.get("/route/{route_id}")
def get_route_index(route_id: int, db: Session = Depends(get_db)) -> dict:
    # Route-level values are deliberately not synthesized from the headline chain.
    item = db.scalar(select(IndexValue).where(IndexValue.route_id == route_id).order_by(IndexValue.date.desc()))
    if not item:
        raise HTTPException(404, "Route-level index has not been computed yet")
    return serialize(item)
