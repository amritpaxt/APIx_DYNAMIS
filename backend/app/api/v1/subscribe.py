from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter

router = APIRouter(prefix="/subscribe", tags=["subscriptions"])


class Subscription(BaseModel):
    webhook: HttpUrl
    threshold_pct: float = 10.0


@router.post("")
def subscribe(subscription: Subscription) -> dict:
    # Persistence/delivery is intentionally deferred until alert authorisation is configured.
    return {"accepted": True, "webhook": str(subscription.webhook), "threshold_pct": subscription.threshold_pct}
