"""Client for the ApeWisdom API."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, Optional

import requests

from ..config import Settings

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class ApeWisdomEntry:
    rank: Optional[int]
    ticker: str
    name: Optional[str]
    mentions: Optional[int]
    upvotes: Optional[int]
    rank_24h_ago: Optional[int]
    mentions_24h_ago: Optional[int]


class ApeWisdomClient:
    """Simple wrapper around the ApeWisdom REST endpoints."""

    API_ROOT = "https://apewisdom.io/api/v1.0"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _request(self, path: str) -> Dict:
        url = f"{self.API_ROOT}/{path.lstrip('/') }"
        headers = {"User-Agent": self.settings.user_agent}
        LOGGER.debug("Fetching %s", url)
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def iter_results(self, filter_name: Optional[str] = None) -> Iterator[ApeWisdomEntry]:
        """Iterate over paginated results for the given filter."""

        filter_name = filter_name or self.settings.apewisdom_filter
        page = 1
        count = 0
        while True:
            payload = self._request(f"filter/{filter_name}/page/{page}")
            results: Iterable[Dict] = payload.get("results", [])
            if not results:
                break
            for item in results:
                yield ApeWisdomEntry(
                    rank=_safe_int(item.get("rank")),
                    ticker=item.get("ticker", "").upper(),
                    name=item.get("name"),
                    mentions=_safe_int(item.get("mentions")),
                    upvotes=_safe_int(item.get("upvotes")),
                    rank_24h_ago=_safe_int(item.get("rank_24h_ago")),
                    mentions_24h_ago=_safe_int(item.get("mentions_24h_ago")),
                )
                count += 1
                if self.settings.ingest_limit and count >= self.settings.ingest_limit:
                    LOGGER.info("Reached ingest limit of %s items", self.settings.ingest_limit)
                    return
            page += 1


def _safe_int(value: Optional[str | int]) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    value = value.strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None
