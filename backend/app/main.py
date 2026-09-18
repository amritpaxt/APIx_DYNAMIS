from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.db.session import SessionLocal, create_schema
from app.ingestion.adapters.synthetic_generator import seed_quotes
from app.index.tornqvist import rebuild_daily_index
from app.pipeline.cleaning import flag_outliers
from app.api.v1 import backtest, elasticity, heatmap, index, routes, subscribe


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_schema()
    if get_settings().seed_on_startup:
        with SessionLocal() as session:
            seed_quotes(session)
            flag_outliers(session)
            rebuild_daily_index(session)
    yield


app = FastAPI(title="APIx", version="0.1.0", description="Transparent airfare price-index prototype", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
for router in (index.router, routes.router, heatmap.router, elasticity.router, backtest.router, subscribe.router):
    app.include_router(router, prefix="/api/v1")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "APIx"}
