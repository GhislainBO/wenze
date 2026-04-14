"""Thin HTTP client for the WENZE backend.

Stdlib-only on purpose — no new dependencies (PRD section 7). Calls are
synchronous; the UI layer runs them in a worker thread and marshals the
result back to the Kivy main loop via `Clock.schedule_once`.
"""
from __future__ import annotations

import json
from typing import List
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# NOTE: 127.0.0.1 works for desktop testing (WSL / localhost).
# Change this to the host machine's LAN IP (e.g. "http://192.168.1.42:8000")
# when running the app on a real Android device so it can reach the backend.
API_BASE_URL = "http://127.0.0.1:8000"

_REQUEST_TIMEOUT_SECONDS = 10


def fetch_services(country: str, city_village: str) -> List[dict]:
    """Return the list of services for the given city.

    Raises on any network, HTTP or JSON error — the caller (services_screen)
    catches and renders the error state.
    """
    query = urlencode({"country": country, "city_village": city_village})
    url = f"{API_BASE_URL}/services?{query}"
    with urlopen(url, timeout=_REQUEST_TIMEOUT_SECONDS) as response:
        payload = response.read().decode("utf-8")
    data = json.loads(payload)
    if not isinstance(data, list):
        raise ValueError("Unexpected response shape: expected a list")
    return data


def log_service_click(service_id: str) -> None:
    """Fire-and-forget POST used for analytics. Raises on any failure;
    the caller runs this in a daemon thread and swallows exceptions."""
    url = f"{API_BASE_URL}/services/{service_id}/log-click"
    req = Request(url, data=b"", method="POST")
    with urlopen(req, timeout=_REQUEST_TIMEOUT_SECONDS) as response:
        response.read()
