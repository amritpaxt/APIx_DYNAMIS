from app.ingestion.adapters.base import SearchRequest, SourceAdapter


class DocumentedStub(SourceAdapter):
    """Named integration placeholder; use an official feed or approved API before enabling."""
    def __init__(self, name: str):
        self.name = name

    def fetch(self, request: SearchRequest) -> list[dict]:
        raise NotImplementedError(f"{self.name} needs an authorised integration; no scraping fallback is enabled.")


ADAPTER_STUBS = {name: DocumentedStub(name) for name in (
    "Air India", "Air India Express", "Akasa Air", "SpiceJet", "MakeMyTrip", "Yatra",
    "EaseMyTrip", "Cleartrip", "Ixigo", "Goibibo",
)}
