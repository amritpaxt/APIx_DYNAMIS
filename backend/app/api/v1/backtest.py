from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.db.models import DGCAMonthlyAvg
from app.db.session import get_db

router = APIRouter(prefix="/backtest", tags=["backtest"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)) -> dict:
    count = db.scalar(select(func.count()).select_from(DGCAMonthlyAvg)) or 0
    return {"status": "ready_for_validation" if count else "pending_dgca_ingest", "dgca_rows": count,
            "message": "DGCA rows are available for matching." if count else "Import an authorised DGCA/MoSPI CSV export before validation."}
