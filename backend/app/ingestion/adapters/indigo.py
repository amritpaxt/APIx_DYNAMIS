from app.ingestion.adapters.base import SearchRequest, SourceAdapter


class IndigoAdapter(SourceAdapter):
    """Documented placeholder for an authorised IndiGo/NDC integration.

    The prototype intentionally does not intercept private endpoints or automate CAPTCHA handling.
    Add an approved API credential and implementation only after a compliance review.
    """

    name = "IndiGo"

    def fetch(self, request: SearchRequest) -> list[dict]:
        raise NotImplementedError("No authorised IndiGo adapter configured; synthetic fallback remains available.")
