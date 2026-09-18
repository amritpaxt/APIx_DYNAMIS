from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class Route(Base):
    __tablename__ = "routes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    origin: Mapped[str] = mapped_column(String(3), index=True)
    destination: Mapped[str] = mapped_column(String(3), index=True)
    dgca_traffic_weight: Mapped[float] = mapped_column(Float)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    __table_args__ = (UniqueConstraint("origin", "destination", name="uq_route_pair"),)
    quotes: Mapped[list["FareQuote"]] = relationship(back_populates="route")


class Carrier(Base):
    __tablename__ = "carriers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    iata_code: Mapped[str] = mapped_column(String(3), unique=True)


class Source(Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    type: Mapped[str] = mapped_column(String(20))
    robots_txt_status: Mapped[str] = mapped_column(String(20), default="unknown")
    last_compliance_check: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class FareQuote(Base):
    __tablename__ = "fare_quotes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"), index=True)
    carrier_id: Mapped[int] = mapped_column(ForeignKey("carriers.id"), index=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), index=True)
    fare_class: Mapped[str] = mapped_column(String(20), default="economy")
    advance_window: Mapped[int] = mapped_column(Integer, index=True)
    departure_date: Mapped[date] = mapped_column(Date, index=True)
    scrape_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    flight_no: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    base_fare: Mapped[float] = mapped_column(Float)
    taxes: Mapped[float] = mapped_column(Float)
    convenience_fee: Mapped[float] = mapped_column(Float, default=0)
    total_fare: Mapped[float] = mapped_column(Float)
    seats_available: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    flight_status: Mapped[str] = mapped_column(String(20), default="operating")
    is_outlier: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_imputed: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    route: Mapped[Route] = relationship(back_populates="quotes")


class EventsAndCosts(Base):
    __tablename__ = "events_and_costs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    event_type: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(Text)
    atf_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    region_affected: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)


class DGCAMonthlyAvg(Base):
    __tablename__ = "dgca_monthly_avg"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"), index=True)
    month: Mapped[date] = mapped_column(Date, index=True)
    avg_fare: Mapped[float] = mapped_column(Float)
    passenger_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    __table_args__ = (UniqueConstraint("route_id", "month", name="uq_dgca_route_month"),)


class IndexValue(Base):
    __tablename__ = "index_values"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    frequency: Mapped[str] = mapped_column(String(12), index=True)
    route_id: Mapped[Optional[int]] = mapped_column(ForeignKey("routes.id"), nullable=True, index=True)
    value: Mapped[float] = mapped_column(Float)
    spread_sub_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float)
    coverage_pct: Mapped[float] = mapped_column(Float)
    outlier_rate: Mapped[float] = mapped_column(Float, default=0)
    chain_break: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = (UniqueConstraint("date", "frequency", "route_id", name="uq_index_value"),)
