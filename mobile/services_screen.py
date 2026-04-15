"""Services listing screen (Phase 2A).

Shows the services available in the user's city. Four states:
loading, empty, error, list. The network call runs in a daemon thread
and widgets are only mutated on the Kivy main loop via Clock.
"""
from __future__ import annotations

import logging
import subprocess
import threading
import webbrowser
from datetime import datetime
from typing import Callable, List, Optional
from urllib.parse import quote

from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from api import fetch_services, log_service_click

_LOG = logging.getLogger(__name__)

# Country → WhatsApp country code (digits only, no '+').
_COUNTRY_CODE = {"RDC": "243", "RC": "242"}


def _parse_iso_datetime(value: str) -> Optional[datetime]:
    """Parse the ISO 8601 strings emitted by FastAPI; None on any failure."""
    try:
        # Python 3.10 fromisoformat doesn't accept a trailing 'Z'; strip it.
        if value.endswith("Z"):
            value = value[:-1]
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def is_active_boost(service: dict) -> bool:
    """True iff the service is boosted AND its boost has not yet expired.

    Used both for sorting (boosted first) and rendering (badge + tinted bg).
    """
    if not service.get("is_boosted"):
        return False
    expiry_raw = service.get("boost_expiry")
    if expiry_raw is None:
        return True
    expiry = (
        _parse_iso_datetime(expiry_raw)
        if isinstance(expiry_raw, str)
        else expiry_raw
    )
    if not isinstance(expiry, datetime):
        return False
    return expiry > datetime.now()


# Official categories -> emoji glyph. Kept for future use (PRD section 3.2);
# emojis render as squares on Kivy/WSL today, so the UI shows text only.
# Mirrors backend Category enum (single source of truth).
CATEGORY_EMOJIS = {
    "Soutien scolaire": "👨\u200d🏫",
    "Réparations & Travaux": "🔧",
    "Beauté & Coiffure": "💇",
    "Jardinage & Entretien": "🌿",
    "Restauration & Bons plans": "🍲",
    "Transport & Livraison": "🚚",
    "Téléphone & Informatique": "📱",
    "Aide ménagère & Lessive": "🧹",
    "Menuiserie & Soudure": "🪑",
    "Mécanique auto & Lavage": "🚗",
}

_CARD_HEIGHT = 180
# Extra space the boost badge occupies above the title.
_BOOST_BADGE_HEIGHT = 24
_BOOST_CARD_HEIGHT = _CARD_HEIGHT + _BOOST_BADGE_HEIGHT + 6
# Subtle warm tint applied behind boosted cards (RGBA, light cream).
_BOOST_BG_RGBA = (1.0, 0.97, 0.86, 1.0)
# Strong dark text so boosted cards stay legible on the cream background.
_BOOST_FG_RGBA = (0.10, 0.10, 0.10, 1.0)


def _format_price(price: int, country: str) -> str:
    """PRD section 3.3: price==0 → 'À discuter', else amount + currency."""
    if price == 0:
        return "À discuter"
    currency = "CDF" if country == "RDC" else "FCFA"
    return f"{price} {currency}"


def _category_label(category: str) -> str:
    # Emojis render as squares on Kivy/WSL; show text only. The mapping is
    # kept in CATEGORY_EMOJIS for the day we have a font that supports them.
    return category


def normalize_phone_number(service: dict, country: str) -> Optional[str]:
    """Return a wa.me-ready digit string (no '+'), or None if unusable."""
    raw = service.get("whatsapp_number") or service.get("phone_number") or ""
    digits = "".join(ch for ch in raw if ch.isdigit())
    if not digits:
        return None
    if digits.startswith(("243", "242")):
        return digits
    code = _COUNTRY_CODE.get(country)
    if code is None:
        return None
    if digits.startswith("0"):
        digits = digits[1:]
    return f"{code}{digits}"


def build_whatsapp_url(service: dict, country: str) -> Optional[str]:
    number = normalize_phone_number(service, country)
    if not number:
        return None
    title = service.get("title", "")
    message = f"Bonjour, je vous contacte via WENZE pour votre service : {title}"
    return f"https://wa.me/{number}?text={quote(message)}"


def open_whatsapp(url: str) -> bool:
    """Try WSL → native Linux → Python webbrowser; return True on first success."""
    # Empty "" after `start` is the window-title placeholder; without it,
    # cmd.exe may treat a quoted URL as the title.
    attempts = (
        ["cmd.exe", "/c", "start", "", url],
        ["xdg-open", url],
    )
    for cmd in attempts:
        try:
            subprocess.run(
                cmd, check=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    try:
        return webbrowser.open(url)
    except Exception as exc:  # noqa: BLE001
        _LOG.info("webbrowser.open failed: %s", exc)
        return False


def log_click(service_id: str) -> None:
    """Fire POST in a daemon thread; never blocks the UI, never raises."""
    if not service_id:
        return

    def _worker() -> None:
        try:
            log_service_click(service_id)
        except Exception as exc:  # noqa: BLE001 - fail silently per spec
            _LOG.info("log_click failed for %s: %s", service_id, exc)

    threading.Thread(target=_worker, daemon=True).start()


def _show_unavailable(card: BoxLayout, button: Button) -> None:
    """Flash a French message on the button for 2s, then restore it."""
    original = button.text
    button.text = "Numéro WhatsApp indisponible."
    button.disabled = True

    def _restore(_dt: float) -> None:
        button.text = original
        button.disabled = False

    Clock.schedule_once(_restore, 2.0)


def _paint_card_background(card: BoxLayout, rgba: tuple) -> None:
    """Draw a solid background rectangle behind a card and keep it in sync."""
    with card.canvas.before:
        Color(*rgba)
        rect = Rectangle(pos=card.pos, size=card.size)

    def _sync(_instance, _value):
        rect.pos = card.pos
        rect.size = card.size

    card.bind(pos=_sync, size=_sync)


def create_service_card(service: dict, country: str) -> Widget:
    """One fixed-height card. Plain labels + a 'Contacter' button wired
    to WhatsApp (Phase 2B). Boosted services get a badge + tinted background
    + slightly larger bold title (Phase 2D)."""
    boosted = is_active_boost(service)
    card_height = _BOOST_CARD_HEIGHT if boosted else _CARD_HEIGHT
    # Dark foreground for boosted labels so text stays readable on the cream
    # background. Passing the Kivy default (white) for non-boosted cards keeps
    # them visually unchanged.
    fg_kwargs = {"color": _BOOST_FG_RGBA} if boosted else {}

    card = BoxLayout(
        orientation="vertical",
        padding=[16, 12, 16, 12],
        spacing=6,
        size_hint_y=None,
        height=card_height,
    )

    if boosted:
        _paint_card_background(card, _BOOST_BG_RGBA)
        card.add_widget(Label(
            text="* A la une *",
            font_size="13sp",
            bold=True,
            size_hint_y=None,
            height=_BOOST_BADGE_HEIGHT,
            **fg_kwargs,
        ))

    card.add_widget(Label(
        text=service.get("title", ""),
        font_size="20sp" if boosted else "18sp",
        bold=boosted,
        size_hint_y=None,
        height=32,
        halign="left",
        valign="middle",
        **fg_kwargs,
    ))
    card.add_widget(Label(
        text=_category_label(service.get("category", "")),
        font_size="14sp",
        size_hint_y=None,
        height=24,
        **fg_kwargs,
    ))
    card.add_widget(Label(
        text=service.get("neighborhood", ""),
        font_size="13sp",
        size_hint_y=None,
        height=22,
        **fg_kwargs,
    ))
    card.add_widget(Label(
        text=_format_price(int(service.get("price", 0)), country),
        font_size="15sp",
        size_hint_y=None,
        height=24,
        **fg_kwargs,
    ))

    contact_btn = Button(
        text="Contacter",
        size_hint_y=None,
        height=48,
    )

    def _on_contact(_btn: Button) -> None:
        try:
            url = build_whatsapp_url(service, country)
        except Exception as exc:  # noqa: BLE001 - never crash the UI
            _LOG.info("build_whatsapp_url failed: %s", exc)
            url = None
        if not url:
            _show_unavailable(card, contact_btn)
            return
        log_click(service.get("id", ""))
        open_whatsapp(url)

    contact_btn.bind(on_release=_on_contact)
    card.add_widget(contact_btn)

    return card


def render_services(container: BoxLayout, services: List[dict], country: str) -> None:
    """Replace the contents of `container` with the list of service cards.

    Always clears first to prevent double-rendering if ever re-entered.
    """
    container.clear_widgets()

    if not services:
        container.add_widget(Label(
            text="Aucun service disponible pour le moment.",
            font_size="16sp",
        ))
        return

    inner = BoxLayout(
        orientation="vertical",
        padding=[0, 8, 0, 8],
        spacing=12,
        size_hint_y=None,
    )
    inner.bind(minimum_height=inner.setter("height"))

    for service in services:
        inner.add_widget(create_service_card(service, country))

    scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
    scroll.add_widget(inner)
    container.add_widget(scroll)


def build_services_screen(
    country: str,
    city: str,
    on_publish: Optional[Callable[[], None]] = None,
) -> Widget:
    """Entry point: loading state first, then async fetch → list/empty/error.

    `on_publish`, when provided, wires the "Publier un Wenze" button. When
    omitted the button is hidden - keeps the screen testable in isolation.
    """
    root = BoxLayout(orientation="vertical", padding=16, spacing=8)

    if on_publish is not None:
        publish_btn = Button(
            text="Publier un Wenze",
            size_hint_y=None,
            height=48,
        )
        publish_btn.bind(on_release=lambda *_: on_publish())
        root.add_widget(publish_btn)

    container = BoxLayout(orientation="vertical")
    container.add_widget(Label(
        text="Chargement des Wenze...",
        font_size="16sp",
    ))
    root.add_widget(container)

    def _on_success(services: List[dict], _dt: float) -> None:
        render_services(container, services, country)

    def _on_error(_dt: float) -> None:
        container.clear_widgets()
        container.add_widget(Label(
            text="Impossible de charger les services.",
            font_size="16sp",
        ))

    def _worker() -> None:
        try:
            services = fetch_services(country, city)
        except Exception:
            Clock.schedule_once(_on_error)
            return
        # Active boosts first; sorted() is stable, so order within each
        # group matches the API response.
        services = sorted(services, key=lambda s: 0 if is_active_boost(s) else 1)
        Clock.schedule_once(lambda dt: _on_success(services, dt))

    threading.Thread(target=_worker, daemon=True).start()
    return root
