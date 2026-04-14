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
from typing import List, Optional
from urllib.parse import quote

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from api import fetch_services, log_service_click

_LOG = logging.getLogger(__name__)

# Country → WhatsApp country code (digits only, no '+').
_COUNTRY_CODE = {"RDC": "243", "RC": "242"}


# Emoji-per-category mapping (PRD section 3.2). Categories unknown to this
# map render as text only — satisfies "emoji if rendering works, otherwise
# text only" without runtime font-capability detection.
CATEGORY_EMOJI = {
    "Soutien scolaire": "📚",
    "Électricité & Maçonnerie": "🔧",
    "Beauté & Coiffure": "💇",
    "Jardinage": "🌿",
    "Pêche & Chasse": "🎣",
    "Restauration & Promo": "🍽️",
    "Transport & Livraison": "🚗",
    "Téléphone & Informatique": "📱",
}

_CARD_HEIGHT = 180


def _format_price(price: int, country: str) -> str:
    """PRD section 3.3: price==0 → 'À discuter', else amount + currency."""
    if price == 0:
        return "À discuter"
    currency = "CDF" if country == "RDC" else "FCFA"
    return f"{price} {currency}"


def _category_label(category: str) -> str:
    emoji = CATEGORY_EMOJI.get(category, "")
    return f"{emoji} {category}".strip()


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
        except Exception as exc:  # noqa: BLE001 — fail silently per spec
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


def create_service_card(service: dict, country: str) -> Widget:
    """One fixed-height card. Plain labels + a 'Contacter' button wired
    to WhatsApp (Phase 2B)."""
    card = BoxLayout(
        orientation="vertical",
        padding=[16, 12, 16, 12],
        spacing=6,
        size_hint_y=None,
        height=_CARD_HEIGHT,
    )

    card.add_widget(Label(
        text=service.get("title", ""),
        font_size="18sp",
        size_hint_y=None,
        height=32,
        halign="left",
        valign="middle",
    ))
    card.add_widget(Label(
        text=_category_label(service.get("category", "")),
        font_size="14sp",
        size_hint_y=None,
        height=24,
    ))
    card.add_widget(Label(
        text=service.get("neighborhood", ""),
        font_size="13sp",
        size_hint_y=None,
        height=22,
    ))
    card.add_widget(Label(
        text=_format_price(int(service.get("price", 0)), country),
        font_size="15sp",
        size_hint_y=None,
        height=24,
    ))

    contact_btn = Button(
        text="Contacter",
        size_hint_y=None,
        height=48,
    )

    def _on_contact(_btn: Button) -> None:
        try:
            url = build_whatsapp_url(service, country)
        except Exception as exc:  # noqa: BLE001 — never crash the UI
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


def build_services_screen(country: str, city: str) -> Widget:
    """Entry point: loading state first, then async fetch → list/empty/error."""
    container = BoxLayout(orientation="vertical", padding=16)
    container.add_widget(Label(
        text="Chargement des Wenze...",
        font_size="16sp",
    ))

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
        Clock.schedule_once(lambda dt: _on_success(services, dt))

    threading.Thread(target=_worker, daemon=True).start()
    return container
