from apscheduler.schedulers.background import BackgroundScheduler
from app.db.session import SessionLocal
from app.ingestion.adapters.synthetic_generator import seed_quotes


def build_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    def refresh_demo_data() -> None:
        with SessionLocal() as session:
            seed_quotes(session, days=1)
    scheduler.add_job(refresh_demo_data, "cron", hour=1, id="synthetic_refresh", replace_existing=True)
    return scheduler
