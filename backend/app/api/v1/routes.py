from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import Route
from app.db.session import get_db

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("")
def list_routes(db: Session = Depends(get_db)) -> list[dict]:
    return [{"id": route.id, "origin": route.origin, "destination": route.destination, "dgca_traffic_weight": route.dgca_traffic_weight,
             "active": route.active} for route in db.scalars(select(Route).order_by(Route.id))]
