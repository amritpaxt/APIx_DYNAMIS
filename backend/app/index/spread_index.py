from collections import defaultdict
from datetime import date
from app.db.models import FareQuote


def daily_spread(quotes: list[FareQuote], day: date) -> float | None:
    values: dict[int, list[float]] = defaultdict(list)
    for quote in quotes:
        if quote.scrape_ts.date() == day and quote.advance_window in (1, 30):
            values[quote.advance_window].append(quote.base_fare + quote.taxes)
    if not values[1] or not values[30]:
        return None
    return round((sum(values[1]) / len(values[1])) / (sum(values[30]) / len(values[30])) * 100, 2)
