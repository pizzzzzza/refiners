"""Runtime configuration helpers for Ape Scout."""

from __future__ import annotations

import functools
import os
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from the environment."""

    apewisdom_filter: str = "all-stocks"
    polygon_api_key: str | None = None
    database_url: str = "sqlite:///./ape_scout.db"
    user_agent: str = "ApeScoutBot/1.0"
    ingest_limit: Optional[int] = None

    @property
    def requires_polygon_key(self) -> None:
        if not self.polygon_api_key:
            raise RuntimeError(
                "A polygon.io API key is required. Set POLYGON_API_KEY in the environment before running."
            )


@functools.cache
def get_settings() -> Settings:
    """Return cached settings populated from the environment."""

    return Settings(
        apewisdom_filter=os.getenv("APEWISDOM_FILTER", "all-stocks"),
        polygon_api_key=os.getenv("POLYGON_API_KEY"),
        database_url=os.getenv("APESCOUT_DATABASE_URL", "sqlite:///./ape_scout.db"),
        user_agent=os.getenv("APESCOUT_USER_AGENT", "ApeScoutBot/1.0"),
        ingest_limit=int(os.getenv("APESCOUT_INGEST_LIMIT", "0")) or None,
    )


def default_ingest_date() -> date:
    """Return today's date in UTC."""

    return date.today()
