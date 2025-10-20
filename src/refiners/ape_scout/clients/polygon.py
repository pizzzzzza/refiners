"""Client for polygon.io."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Optional

import requests

from ..config import Settings

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class PolygonTickerDetails:
    market_cap: Optional[float]
    description: Optional[str]
    sic_description: Optional[str]


class PolygonClient:
    """Minimal polygon.io REST client."""

    API_ROOT = "https://api.polygon.io"

    def __init__(self, settings: Settings) -> None:
        if not settings.polygon_api_key:
            raise RuntimeError("Polygon API key missing. Set POLYGON_API_KEY in the environment.")
        self.settings = settings

    def _request(self, path: str, params: Optional[Dict[str, str]] = None) -> Dict:
        params = dict(params or {})
        params["apiKey"] = self.settings.polygon_api_key or ""
        url = f"{self.API_ROOT}{path}"
        LOGGER.debug("Polygon request %s", url)
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_details(self, ticker: str) -> PolygonTickerDetails:
        payload = self._request("/v3/reference/tickers", {"ticker": ticker.upper(), "limit": "1"})
        results = payload.get("results", [])
        if not results:
            return PolygonTickerDetails(market_cap=None, description=None, sic_description=None)
        result = results[0]
        return PolygonTickerDetails(
            market_cap=result.get("market_cap"),
            description=result.get("description"),
            sic_description=result.get("sic_description"),
        )

    def get_previous_close(self, ticker: str, target_date: date, lookback: int = 5) -> Optional[float]:
        current = target_date
        for _ in range(lookback):
            date_str = current.isoformat()
            payload = self._request(
                f"/v2/aggs/ticker/{ticker.upper()}/range/1/day/{date_str}/{date_str}",
                {"adjusted": "true", "sort": "desc", "limit": "1"},
            )
            results = payload.get("results") or []
            if results:
                return results[0].get("c")
            current = current - timedelta(days=1)
        return None
