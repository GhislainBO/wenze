"""Local persistence of the onboarding city choice.

A single JSON file under the app's user_data_dir (provided by Kivy) so it works
the same way on desktop and Android. Keeping it here avoids dragging in any
dependency beyond stdlib.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, TypedDict

CITY_FILE_NAME = "city.json"


class CityChoice(TypedDict):
    country: str  # "RDC" or "RC"
    city: str     # "Kinshasa" or "Brazzaville"


def _city_path(user_data_dir: str) -> Path:
    return Path(user_data_dir) / CITY_FILE_NAME


def load_city(user_data_dir: str) -> Optional[CityChoice]:
    """Return the stored choice, or None on first launch / corrupt file."""
    path = _city_path(user_data_dir)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    country = data.get("country")
    city = data.get("city")
    if country not in ("RDC", "RC") or not isinstance(city, str):
        return None
    return {"country": country, "city": city}


def save_city(user_data_dir: str, country: str, city: str) -> None:
    """Persist the choice atomically."""
    path = _city_path(user_data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps({"country": country, "city": city}, ensure_ascii=False)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(path)
