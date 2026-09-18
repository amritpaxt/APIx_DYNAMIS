# APIx

APIx is a transparent prototype for a high-frequency Indian domestic airfare price index. It starts with reproducible synthetic data so the complete data-quality and index chain can be reviewed without claiming live supplier coverage.

## Run the backend

From `backend`, create a virtual environment, install `requirements.txt`, and run `uvicorn app.main:app --reload`. The API will seed 60 days of explicitly marked synthetic fares and expose Swagger at `/docs`.

## Run the dashboard

From `frontend`, run `pnpm install` then `pnpm dev`. Set `VITE_API_BASE_URL` if the API is not at `http://localhost:8000/api/v1`.

## Ethics and source status

The real provider adapters are intentionally disabled. They must use an authorised API/feed after a robots.txt and terms review; this project does not evade CAPTCHAs, access controls, or rate limits. The source-health page distinguishes fixture data from approved integrations.

## Implemented core

- TimescaleDB-ready `fare_quotes` schema plus every named supporting table
- Deterministic synthetic generator, cleaning rules, MAD review flags, and explicit flight statuses
- Daily chained Törnqvist calculation and coverage/outlier confidence metadata
- FastAPI routes for index, routes, heatmap, elasticity, backtest status, and subscriptions
- React dashboard shell with trend, spread, heatmap, elasticity, source-health, backtest, and explainer views

Backtest ingestion, forecasting, RAG, alerts, and real provider feeds remain deliberately staged extensions.

An approved public-data entry point is included at `backend/app/backtest/dgca_ingest.py`: it imports a downloaded MoSPI/DGCA CSV with `origin`, `destination`, `month`, `avg_fare`, and optional `passenger_count` columns. It makes no assumption about an undocumented portal API.
