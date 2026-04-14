"""WENZE mobile - Kivy app entry point.

First launch shows a one-tap city picker (Kinshasa / Brazzaville). The choice
is persisted locally and never asked again. Once a city is chosen, the app
lands on the services listing screen (Phase 2A).

Constraints (PRD section 7):
- No KivyMD.
- Simple UI only, no complex logic in the UI layer.
- Android / Buildozer compatible (stdlib only + Kivy).
"""
from __future__ import annotations

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from publish_screen import build_publish_screen
from services_screen import build_services_screen
from storage import load_city, save_city


# --- UI builders (pure functions - easier to test, keep UI layer thin) -----

def build_onboarding(on_select) -> BoxLayout:
    """Screen shown on first launch (PRD section 2)."""
    root = BoxLayout(orientation="vertical", padding=[40, 60, 40, 60], spacing=24)

    root.add_widget(Label(
        text="Voir les Wenze près de :",
        font_size="22sp",
        size_hint_y=None,
        height=80,
    ))

    kinshasa = Button(
        text="Kinshasa 🇨🇩",
        font_size="20sp",
        size_hint_y=None,
        height=120,
    )
    brazzaville = Button(
        text="Brazzaville 🇨🇬",
        font_size="20sp",
        size_hint_y=None,
        height=120,
    )
    kinshasa.bind(on_release=lambda *_: on_select("RDC", "Kinshasa"))
    brazzaville.bind(on_release=lambda *_: on_select("RC", "Brazzaville"))

    root.add_widget(kinshasa)
    root.add_widget(brazzaville)
    # Push the buttons up; empty stretch pads the bottom.
    root.add_widget(BoxLayout())
    return root


# --- App ------------------------------------------------------------------

class WenzeApp(App):
    title = "WENZE"

    def build(self):
        # Outer container lets us swap the active view without rebuilding the app.
        self._container = BoxLayout()
        self._render()
        return self._container

    def _render(self) -> None:
        self._container.clear_widgets()
        saved = load_city(self.user_data_dir)
        if saved is None:
            self._container.add_widget(build_onboarding(self._on_city_selected))
            return
        self._container.add_widget(build_services_screen(
            saved["country"],
            saved["city"],
            on_publish=self._show_publish,
        ))

    def _show_publish(self) -> None:
        saved = load_city(self.user_data_dir)
        if saved is None:
            # Shouldn't happen - guard anyway.
            self._render()
            return
        self._container.clear_widgets()
        self._container.add_widget(build_publish_screen(
            country=saved["country"],
            city=saved["city"],
            on_back=self._render,
            on_published=self._render,
        ))

    def _on_city_selected(self, country: str, city: str) -> None:
        save_city(self.user_data_dir, country, city)
        self._render()


if __name__ == "__main__":
    WenzeApp().run()
