from __future__ import annotations
from collections import defaultdict
from datetime import date
from math import exp, log
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from app.config import get_settings
from app.db.models import FareQuote, IndexValue, Route
from app.index.confidence import score
from app.index.spread_index import daily_spread
from app.index.weights import booking_window_weights, traffic_weights
from app.pipeline.cleaning import index_eligible


def _route_prices(quotes: list[FareQuote], weights: dict[int, float]) -> dict[int, float]:
    by_route_window: dict[tuple[int, int], list[float]] = defaultdict(list)
    for quote in quotes:
        if index_eligible(quote):
            # CTA/OTA convenience charges are excluded by design.
            by_route_window[(quote.route_id, quote.advance_window)].append(quote.base_fare + quote.taxes)
    result: dict[int, float] = {}
    routes = {route_id for route_id, _ in by_route_window}
    for route_id in routes:
        parts = [(weights[window], sum(values) / len(values)) for (rid, window), values in by_route_window.items()
                 if rid == route_id and window in weights]
        if parts:
            scale = sum(weight for weight, _ in parts)
            result[route_id] = sum(weight * value for weight, value in parts) / scale
    return result


def tornqvist_step(previous_index: float, previous_prices: dict[int, float], current_prices: dict[int, float], route_weights: dict[int, float]) -> float:
    """One superlative chained step using average-period route weights."""
    usable = [route_id for route_id in current_prices if route_id in previous_prices and current_prices[route_id] > 0 and previous_prices[route_id] > 0]
    normalizer = sum(route_weights[route_id] for route_id in usable)
    if not normalizer:
        return previous_index
    log_change = sum(route_weights[route_id] / normalizer * log(current_prices[route_id] / previous_prices[route_id]) for route_id in usable)
    return previous_index * exp(log_change)


def rebuild_daily_index(session: Session, base_value: float = 100.0) -> int:
    """Persist chained daily Törnqvist values and explicit confidence metadata."""
    all_quotes = list(session.scalars(select(FareQuote).order_by(FareQuote.scrape_ts)))
    if not all_quotes:
        return 0
    settings = get_settings()
    window_weights = booking_window_weights(all_quotes)
    route_weights = traffic_weights(session)
    routes = list(session.scalars(select(Route).where(Route.active.is_(True))))
    days = sorted({quote.scrape_ts.date() for quote in all_quotes})
    session.execute(delete(IndexValue).where(IndexValue.frequency == "daily", IndexValue.route_id.is_(None)))
    previous_prices: dict[int, float] | None = None
    previous_index = base_value
    written = 0
    for day in days:
        todays = [quote for quote in all_quotes if quote.scrape_ts.date() == day]
        prices = _route_prices(todays, window_weights)
        eligible = [q for q in todays if index_eligible(q)]
        cells = {(q.route_id, q.advance_window) for q in eligible}
        quality = score(len(cells), len(routes) * len(window_weights), sum(q.is_outlier for q in todays), len(todays), settings.coverage_threshold)
        if previous_prices is None or quality.chain_break:
            value = previous_index
        else:
            value = tornqvist_step(previous_index, previous_prices, prices, route_weights)
        session.add(IndexValue(date=day, frequency="daily", route_id=None, value=round(value, 4), spread_sub_index=daily_spread(eligible, day),
                               confidence_score=quality.score, coverage_pct=quality.coverage_pct, outlier_rate=quality.outlier_rate, chain_break=quality.chain_break))
        previous_index = value
        if not quality.chain_break:
            previous_prices = prices
        written += 1
    session.commit()
    return written
