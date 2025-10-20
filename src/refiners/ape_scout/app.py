"""FastAPI application exposing the Ape Scout dashboard."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from .config import get_settings
from .database import create_all, get_session
from .models import Sector, Stock, StockMetric

BASE_DIR = Path(__file__).resolve().parent


def create_app() -> FastAPI:
    create_all()
    app = FastAPI(title="Ape Scout", default_response_class=HTMLResponse)

    templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

    def _session_dep():
        db = get_session()
        try:
            yield db
        finally:
            db.close()

    @app.get("/", response_class=HTMLResponse)
    def index(
        request: Request,
        page: int = Query(1, ge=1),
        page_size: int = Query(25, ge=10, le=100),
        market_cap_min: Optional[float] = Query(None, ge=0),
        market_cap_max: Optional[float] = Query(None, ge=0),
        close_min: Optional[float] = Query(None, ge=0),
        close_max: Optional[float] = Query(None, ge=0),
        mentions_min: Optional[int] = Query(None, ge=0),
        mentions_max: Optional[int] = Query(None, ge=0),
        upvotes_min: Optional[int] = Query(None, ge=0),
        upvotes_max: Optional[int] = Query(None, ge=0),
        days: int = Query(30, ge=7, le=180),
        sectors: Optional[List[str]] = Query(None),
        consistent_mentions: bool = Query(False),
        session: Session = Depends(_session_dep),
    ) -> HTMLResponse:
        latest_date = session.scalar(select(func.max(StockMetric.as_of_date)))
        if latest_date is None:
            return templates.TemplateResponse(
                "empty.html",
                {"request": request, "settings": get_settings(), "message": "数据库中还没有数据，请先运行采集任务。"},
            )

        filters = [StockMetric.as_of_date == latest_date]

        def _range_filter(column, minimum, maximum):
            if minimum is not None:
                filters.append(column >= minimum)
            if maximum is not None:
                filters.append(column <= maximum)

        _range_filter(StockMetric.market_cap, market_cap_min, market_cap_max)
        _range_filter(StockMetric.close_price, close_min, close_max)
        _range_filter(StockMetric.mentions, mentions_min, mentions_max)
        _range_filter(StockMetric.upvotes, upvotes_min, upvotes_max)

        base_query = (
            select(Stock, StockMetric)
            .join(StockMetric, StockMetric.stock_id == Stock.id)
            .where(and_(*filters))
        )

        if sectors:
            sector_ids = (
                select(Stock.id)
                .join(Stock.sectors)
                .where(Sector.name.in_(sectors))
                .group_by(Stock.id)
            )
            base_query = base_query.where(Stock.id.in_(sector_ids))

        trend_start = latest_date - timedelta(days=days - 1)

        if consistent_mentions:
            consistent_ids = (
                select(StockMetric.stock_id)
                .where(
                    StockMetric.as_of_date >= trend_start,
                    StockMetric.as_of_date <= latest_date,
                    StockMetric.mentions > 0,
                )
                .group_by(StockMetric.stock_id)
                .having(func.count() >= days)
            )
            base_query = base_query.where(Stock.id.in_(consistent_ids))

        count_query = select(func.count()).select_from(base_query.subquery())
        total = session.scalar(count_query) or 0

        base_query = base_query.order_by(StockMetric.rank.asc().nullslast(), StockMetric.mentions.desc())

        offset = (page - 1) * page_size
        rows = session.execute(base_query.offset(offset).limit(page_size)).all()
        summaries: List[Dict] = []
        for stock, metric in rows:
            trend_rows = session.execute(
                select(StockMetric.as_of_date, StockMetric.mentions)
                .where(
                    StockMetric.stock_id == stock.id,
                    StockMetric.as_of_date >= trend_start,
                    StockMetric.as_of_date <= latest_date,
                )
                .order_by(StockMetric.as_of_date)
            ).all()
            trend = [
                {
                    "date": rec.as_of_date.isoformat(),
                    "mentions": rec.mentions or 0,
                }
                for rec in trend_rows
            ]

            summaries.append(
                {
                    "stock": stock,
                    "metric": metric,
                    "trend": trend,
                    "sectors": [sector.name for sector in stock.sectors],
                }
            )

        pages = max((total + page_size - 1) // page_size, 1)

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "items": summaries,
                "page": page,
                "page_size": page_size,
                "pages": pages,
                "total": total,
                "latest_date": latest_date,
                "days": days,
                "sectors": sectors or [],
                "available_sectors": _list_sectors(session),
                "consistent_mentions": consistent_mentions,
                "filters": {
                    "market_cap_min": market_cap_min,
                    "market_cap_max": market_cap_max,
                    "close_min": close_min,
                    "close_max": close_max,
                    "mentions_min": mentions_min,
                    "mentions_max": mentions_max,
                    "upvotes_min": upvotes_min,
                    "upvotes_max": upvotes_max,
                },
            },
        )

    return app


def _list_sectors(session: Session) -> List[str]:
    return session.scalars(select(Sector.name).order_by(Sector.name)).all()
