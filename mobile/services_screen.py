"""Services listing screen (Phase 2A).

Shows the services available in the user's city. Four states:
loading, empty, error, list. The network call runs in a daemon thread
and widgets are only mutated on the Kivy main loop via Clock.
"""
from __future__ import annotations

import threading
from typing import List

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from api import fetch_services


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


def create_service_card(service: dict, country: str) -> Widget:
    """One fixed-height card. Plain labels + an inert 'Contacter' button.

    The button is deliberately inert in Phase 2A; WhatsApp wiring lands
    in Phase 2B.
    """
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
    # Phase 2B will wire this to WhatsApp + log-click.
    contact_btn.bind(on_release=lambda *_: None)
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
