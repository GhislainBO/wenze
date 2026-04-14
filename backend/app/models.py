"""SQLModel table definitions for WENZE.

Schema mirrors PRD section 5 (Data Model). Category values are kept in French
because they double as UI labels (PRD section 3.2).

Note: we intentionally do not `from __future__ import annotations` here —
SQLModel's `Relationship()` resolves related-class names at import time and
cannot parse lazy string annotations like `list["Service"]`.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Category(str, Enum):
    """Service categories — French labels preserved for UI rendering."""

    SOUTIEN_SCOLAIRE = "Soutien scolaire"
    ELECTRICITE_MACONNERIE = "Électricité & Maçonnerie"
    BEAUTE_COIFFURE = "Beauté & Coiffure"
    JARDINAGE = "Jardinage"
    PECHE_CHASSE = "Pêche & Chasse"
    RESTAURATION_PROMO = "Restauration & Promo"
    TRANSPORT_LIVRAISON = "Transport & Livraison"
    TELEPHONE_INFORMATIQUE = "Téléphone & Informatique"


class ServiceStatus(str, Enum):
    """Lifecycle state of a service listing."""

    ACTIVE = "active"
    INACTIVE = "inactive"


def _new_uuid() -> str:
    return str(uuid.uuid4())


class User(SQLModel, table=True):
    """Service provider / end user."""

    id: str = Field(default_factory=_new_uuid, primary_key=True)
    name: str
    phone_number: str
    country: str  # "RDC" or "RC"
    city_village: str
    neighborhood: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    services: List["Service"] = Relationship(back_populates="user")


class Service(SQLModel, table=True):
    """A local service listed on the marketplace."""

    id: str = Field(default_factory=_new_uuid, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str
    category: Category
    description: str
    price: int  # 0 means the price is negotiable ("À discuter")
    country: str  # "RDC" or "RC"
    city_village: str
    neighborhood: str
    whatsapp_number: str
    phone_number: str
    is_boosted: bool = Field(default=False)
    boost_expiry: Optional[datetime] = Field(default=None)
    status: ServiceStatus = Field(default=ServiceStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="services")
