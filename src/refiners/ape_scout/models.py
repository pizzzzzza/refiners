"""Database models for Ape Scout."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Iterable

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class TimestampMixin:
    """Mixin adding creation timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc)
    )


class Stock(Base, TimestampMixin):
    """Tracked stock tickers."""

    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    metrics: Mapped[list["StockMetric"]] = relationship(back_populates="stock", cascade="all, delete-orphan")
    sectors: Mapped[list["Sector"]] = relationship(
        secondary="stock_sectors",
        back_populates="stocks",
        lazy="selectin",
    )

    def set_sectors(self, sectors: Iterable["Sector"]) -> None:
        self.sectors = list({sector for sector in sectors})


class Sector(Base):
    """Industry categories assigned to stocks."""

    __tablename__ = "sectors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)

    stocks: Mapped[list[Stock]] = relationship(
        secondary="stock_sectors",
        back_populates="sectors",
    )


class StockSector(Base):
    """Association table mapping stocks to sectors."""

    __tablename__ = "stock_sectors"

    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), primary_key=True)
    sector_id: Mapped[int] = mapped_column(ForeignKey("sectors.id", ondelete="CASCADE"), primary_key=True)


class StockMetric(Base, TimestampMixin):
    """Daily metrics collected from ApeWisdom and polygon.io."""

    __tablename__ = "stock_metrics"
    __table_args__ = (UniqueConstraint("stock_id", "as_of_date", name="uq_stock_metrics_stock_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    as_of_date: Mapped[date] = mapped_column(Date, index=True)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mentions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    upvotes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mentions_prev: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rank_prev: Mapped[int | None] = mapped_column(Integer, nullable=True)
    market_cap: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    close_price: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True)

    stock: Mapped[Stock] = relationship(back_populates="metrics")
