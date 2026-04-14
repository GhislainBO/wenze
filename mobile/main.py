"""WENZE mobile — Kivy onboarding (Phase 1).

First launch shows a one-tap city picker (Kinshasa / Brazzaville). The choice
is persisted locally and never asked again. A tiny placeholder "home" screen
confirms the selection for now; the real home view will arrive in Phase 2.

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

from storage import load_city, save_city


# --- UI builders (pure functions — easier to test, keep UI layer thin) -----

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


def build_home_placeholder(country: str, city: str) -> BoxLayout:
    """Temporary screen shown after a city has been chosen."""
    flag = "🇨🇩" if country == "RDC" else "🇨🇬"
    root = BoxLayout(orientation="vertical", padding=40, spacing=16)
    root.add_widget(Label(
        text=f"Bienvenue à {city} {flag}",
        font_size="24sp",
    ))
    root.add_widget(Label(
        text="(Écran d'accueil — à venir dans la prochaine phase)",
        font_size="14sp",
    ))
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
        if saved is not None:
            self._container.add_widget(
                build_home_placeholder(saved["country"], saved["city"])
            )
        else:
            self._container.add_widget(build_onboarding(self._on_city_selected))

    def _on_city_selected(self, country: str, city: str) -> None:
        save_city(self.user_data_dir, country, city)
        self._render()


if __name__ == "__main__":
    WenzeApp().run()
