"""High-level services for data ingestion."""

from __future__ import annotations

import logging
from datetime import date
from typing import Dict

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .classification import classify_sectors
from .clients.apewisdom import ApeWisdomClient
from .clients.polygon import PolygonClient
from .config import Settings, default_ingest_date, get_settings
from .database import create_all, session_scope
from .models import Sector, Stock, StockMetric

LOGGER = logging.getLogger(__name__)


def run_ingestion(target_date: date | None = None, settings: Settings | None = None) -> None:
    """Fetch ApeWisdom data and enrich with polygon.io metrics."""

    create_all()
    settings = settings or get_settings()
    target_date = target_date or default_ingest_date()
    LOGGER.info("Starting ingestion for %s", target_date.isoformat())

    aw_client = ApeWisdomClient(settings)
    polygon_client = PolygonClient(settings)

    with session_scope() as session:
        _ingest(session, aw_client, polygon_client, target_date)


def _ingest(session: Session, aw_client: ApeWisdomClient, polygon_client: PolygonClient, target_date: date) -> None:
    sector_cache: Dict[str, Sector] = _load_sector_cache(session)
    ticker_details_cache: Dict[str, Dict] = {}

    for entry in aw_client.iter_results():
        if not entry.ticker:
            continue
        stock = _get_or_create_stock(session, entry.ticker, entry.name)

        if entry.name and stock.name != entry.name:
            stock.name = entry.name

        details = ticker_details_cache.get(entry.ticker)
        if details is None:
            details_obj = polygon_client.get_details(entry.ticker)
            details = {
                "market_cap": details_obj.market_cap,
                "description": details_obj.description,
                "sic_description": details_obj.sic_description,
            }
            ticker_details_cache[entry.ticker] = details

        sectors = classify_sectors(details.get("description"), details.get("sic_description"))
        stock.set_sectors([_get_or_create_sector(session, sector_cache, name) for name in sectors])

        close_price = polygon_client.get_previous_close(entry.ticker, target_date)

        metric = StockMetric(
            stock=stock,
            as_of_date=target_date,
            rank=entry.rank,
            mentions=entry.mentions,
            upvotes=entry.upvotes,
            mentions_prev=entry.mentions_24h_ago,
            rank_prev=entry.rank_24h_ago,
            market_cap=details.get("market_cap"),
            close_price=close_price,
        )
        try:
            session.add(metric)
            session.flush()
        except IntegrityError:
            session.rollback()
            existing = session.scalar(
                select(StockMetric).where(StockMetric.stock_id == stock.id, StockMetric.as_of_date == target_date)
            )
            if existing:
                LOGGER.debug("Updating metrics for %s on %s", stock.ticker, target_date)
                existing.rank = entry.rank
                existing.mentions = entry.mentions
                existing.upvotes = entry.upvotes
                existing.mentions_prev = entry.mentions_24h_ago
                existing.rank_prev = entry.rank_24h_ago
                existing.market_cap = details.get("market_cap")
                existing.close_price = close_price
            else:
                LOGGER.warning("Failed to persist metrics for %s", stock.ticker)


def _get_or_create_stock(session: Session, ticker: str, name: str | None) -> Stock:
    stock = session.scalar(select(Stock).where(Stock.ticker == ticker))
    if stock:
        return stock
    stock = Stock(ticker=ticker, name=name)
    session.add(stock)
    session.flush()
    return stock


def _get_or_create_sector(session: Session, cache: Dict[str, Sector], name: str) -> Sector:
    if name in cache:
        return cache[name]
    sector = session.scalar(select(Sector).where(Sector.name == name))
    if sector is None:
        sector = Sector(name=name)
        session.add(sector)
        session.flush()
    cache[name] = sector
    return sector


def _load_sector_cache(session: Session) -> Dict[str, Sector]:
    sectors = session.scalars(select(Sector)).all()
    return {sector.name: sector for sector in sectors}
