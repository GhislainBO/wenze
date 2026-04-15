"""Publish-a-service screen (Phase 2C).

Simple text-only form that POSTs a new service to the backend. Uses the
locally-persisted city choice for country/city_village and an anonymous
placeholder user_id until Phase 3 introduces real authentication.
"""
from __future__ import annotations

import logging
import threading
from typing import Callable, Optional

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from api import create_service

_LOG = logging.getLogger(__name__)

# Placeholder user id - the backend seeds a matching row so POST /services
# succeeds. Replaced when Phase 3 adds authentication.
ANONYMOUS_USER_ID = "00000000-0000-0000-0000-000000000000"

# Canonical French category labels - mirrors backend Category enum
# (single source of truth in backend/app/models.py). Order matters:
# it's the order shown in the Spinner dropdown. Keep in sync if the
# backend list changes.
CATEGORIES = (
    "Soutien scolaire",
    "Réparations & Travaux",
    "Beauté & Coiffure",
    "Jardinage & Entretien",
    "Restauration & Bons plans",
    "Transport & Livraison",
    "Téléphone & Informatique",
    "Aide ménagère & Lessive",
    "Menuiserie & Soudure",
    "Mécanique auto & Lavage",
)

_CATEGORY_PLACEHOLDER = "Choisir une catégorie"


def _clean_phone(raw: str) -> str:
    """Strip spaces, dashes, dots, parentheses (but keep the leading '+')."""
    return "".join(ch for ch in raw if ch.isdigit() or ch == "+")


def _count_digits(raw: str) -> int:
    return sum(1 for ch in raw if ch.isdigit())


def _field_row(label_text: str, widget: Widget, height: int = 44) -> BoxLayout:
    """Label + input, stacked vertically. Fixed height for predictable layout."""
    row = BoxLayout(
        orientation="vertical",
        size_hint_y=None,
        height=24 + height,
        spacing=4,
    )
    row.add_widget(Label(
        text=label_text,
        font_size="14sp",
        size_hint_y=None,
        height=20,
        halign="left",
        valign="middle",
    ))
    row.add_widget(widget)
    return row


def _validate(
    title: str,
    category: str,
    neighborhood: str,
    price_raw: str,
    whatsapp_raw: str,
) -> Optional[str]:
    """Return a French error message, or None if the form is valid."""
    if not title.strip():
        return "Le titre est obligatoire."
    if category == _CATEGORY_PLACEHOLDER or category not in CATEGORIES:
        return "La catégorie est obligatoire."
    if not neighborhood.strip():
        return "Le quartier est obligatoire."
    price_stripped = price_raw.strip()
    if not price_stripped:
        return "Le prix est obligatoire (0 pour 'À discuter')."
    try:
        price = int(price_stripped)
    except ValueError:
        return "Le prix doit être un nombre entier."
    if price < 0:
        return "Le prix doit être supérieur ou égal à 0."
    cleaned_phone = _clean_phone(whatsapp_raw)
    if not cleaned_phone:
        return "Le numéro WhatsApp est obligatoire."
    # Local Kinshasa/Brazzaville numbers are 9+ digits after the country code;
    # insist on at least 9 digits to catch obvious typos.
    if _count_digits(cleaned_phone) < 9:
        return "Le numéro WhatsApp semble incomplet."
    return None


def build_publish_screen(
    country: str,
    city: str,
    on_back: Callable[[], None],
    on_published: Callable[[], None],
) -> Widget:
    """Build the publish form. `on_back` returns to the list unchanged;
    `on_published` returns to the list and triggers a refresh."""
    root = BoxLayout(orientation="vertical", padding=16, spacing=12)

    root.add_widget(Label(
        text=f"Publier un Wenze à {city}",
        font_size="20sp",
        size_hint_y=None,
        height=32,
    ))

    # --- form fields ------------------------------------------------------
    title_input = TextInput(multiline=False, size_hint_y=None, height=44)
    category_spinner = Spinner(
        text=_CATEGORY_PLACEHOLDER,
        values=CATEGORIES,
        size_hint_y=None,
        height=44,
    )
    neighborhood_input = TextInput(multiline=False, size_hint_y=None, height=44)
    price_input = TextInput(
        multiline=False,
        size_hint_y=None,
        height=44,
        input_filter="int",
        hint_text="0 pour 'À discuter'",
    )
    whatsapp_input = TextInput(
        multiline=False,
        size_hint_y=None,
        height=44,
        hint_text="+243 …",
    )
    description_input = TextInput(
        multiline=True,
        size_hint_y=None,
        height=100,
    )

    form = BoxLayout(
        orientation="vertical",
        spacing=10,
        size_hint_y=None,
    )
    form.bind(minimum_height=form.setter("height"))
    form.add_widget(_field_row("Titre", title_input))
    form.add_widget(_field_row("Catégorie", category_spinner))
    form.add_widget(_field_row("Quartier", neighborhood_input))
    form.add_widget(_field_row("Prix", price_input))
    form.add_widget(_field_row("Numéro WhatsApp", whatsapp_input))
    form.add_widget(_field_row("Description", description_input, height=100))

    scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
    scroll.add_widget(form)
    root.add_widget(scroll)

    # --- status line + action buttons ------------------------------------
    status_label = Label(
        text="",
        font_size="14sp",
        size_hint_y=None,
        height=24,
    )
    root.add_widget(status_label)

    actions = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=52,
        spacing=12,
    )
    back_btn = Button(text="Retour")
    submit_btn = Button(text="Valider")
    actions.add_widget(back_btn)
    actions.add_widget(submit_btn)
    root.add_widget(actions)

    # --- wiring ----------------------------------------------------------
    # Mutable flag to guard against double submissions. Using a list so the
    # inner closures can mutate it without `nonlocal` declarations.
    submitting = [False]

    def _set_idle() -> None:
        submit_btn.disabled = False
        submit_btn.text = "Valider"

    def _on_success(_dt: float) -> None:
        status_label.text = "Wenze publié avec succès !"
        # Small delay so the user sees the success message before navigating.
        Clock.schedule_once(lambda _: on_published(), 0.6)

    def _on_error(_dt: float) -> None:
        submitting[0] = False
        _set_idle()
        status_label.text = "Erreur lors de la publication. Veuillez réessayer."

    def _submit(_btn: Button) -> None:
        if submitting[0]:
            return

        error = _validate(
            title_input.text,
            category_spinner.text,
            neighborhood_input.text,
            price_input.text,
            whatsapp_input.text,
        )
        if error is not None:
            status_label.text = error
            return

        cleaned_phone = _clean_phone(whatsapp_input.text)
        payload = {
            "user_id": ANONYMOUS_USER_ID,
            "title": title_input.text.strip(),
            "category": category_spinner.text,
            "description": description_input.text.strip(),
            "price": int(price_input.text.strip()),
            "country": country,
            "city_village": city,
            "neighborhood": neighborhood_input.text.strip(),
            "whatsapp_number": cleaned_phone,
            "phone_number": cleaned_phone,
        }

        submitting[0] = True
        submit_btn.disabled = True
        submit_btn.text = "Publication en cours..."
        status_label.text = ""

        def _worker() -> None:
            try:
                create_service(payload)
            except Exception as exc:  # noqa: BLE001 - surface a generic message
                _LOG.info("create_service failed: %s", exc)
                Clock.schedule_once(_on_error)
                return
            Clock.schedule_once(_on_success)

        threading.Thread(target=_worker, daemon=True).start()

    submit_btn.bind(on_release=_submit)
    back_btn.bind(on_release=lambda *_: on_back())

    return root
