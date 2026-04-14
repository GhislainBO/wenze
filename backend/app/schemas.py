"""Request schemas for the WENZE API.

Table models in `app.models` double as response schemas; this file holds the
input-only shapes (fields the client sends, without server-controlled defaults
like `id`, `created_at`, `is_boosted`, `status`).
"""
from __future__ import annotations

from sqlmodel import SQLModel

from app.models import Category


class ServiceCreate(SQLModel):
    """Payload for POST /services."""

    user_id: str
    title: str
    category: Category
    description: str
    price: int
    country: str  # "RDC" or "RC"
    city_village: str
    neighborhood: str
    whatsapp_number: str
    phone_number: str
