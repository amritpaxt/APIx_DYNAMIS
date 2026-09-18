from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class SearchRequest:
    origin: str
    destination: str
    departure_date: date
    advance_window: int
    requested_at: datetime


class SourceAdapter(ABC):
    """Ethical adapter contract. Implementations must respect robots.txt and source terms."""
    name: str

    @abstractmethod
    def fetch(self, request: SearchRequest) -> list[dict]:
        """Return raw supplier records; never bypass CAPTCHAs or access controls."""
