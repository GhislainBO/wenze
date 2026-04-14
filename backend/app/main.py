"""FastAPI application entry point for WENZE.

Phase 1 endpoints (PRD section 4.2):
- GET  /services                     list services, filterable by country/city/category
- POST /services                     create a service
- POST /services/{id}/log-click      record a click event
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Session, col, select

from app.database import engine, get_session, init_db
from app.models import Category, Service, User
from app.schemas import ServiceCreate

logger = logging.getLogger("wenze")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    """SQLite does not enforce foreign keys by default; turn it on per connection."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


app = FastAPI(title="WENZE API", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/services", response_model=list[Service])
def list_services(
    country: Optional[str] = None,
    city_village: Optional[str] = None,
    category: Optional[Category] = None,
    session: Session = Depends(get_session),
) -> list[Service]:
    query = select(Service)
    if country is not None:
        query = query.where(Service.country == country)
    if city_village is not None:
        query = query.where(Service.city_village == city_village)
    if category is not None:
        query = query.where(Service.category == category)
    # Boosted listings first, then most recent.
    query = query.order_by(
        col(Service.is_boosted).desc(),
        col(Service.created_at).desc(),
    )
    return session.exec(query).all()


@app.post(
    "/services",
    response_model=Service,
    status_code=status.HTTP_201_CREATED,
)
def create_service(
    payload: ServiceCreate,
    session: Session = Depends(get_session),
) -> Service:
    user = session.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    service = Service(**payload.model_dump())
    session.add(service)
    session.commit()
    session.refresh(service)
    return service


@app.post("/services/{service_id}/log-click", status_code=status.HTTP_200_OK)
def log_click(
    service_id: str,
    session: Session = Depends(get_session),
) -> dict[str, str]:
    service = session.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    logger.info("click: service_id=%s", service_id)
    return {"status": "ok"}
