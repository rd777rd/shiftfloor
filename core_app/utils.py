"""
Shared utilities used across apps: geo-distance matching (no paid geocoding
API — coordinates are stored on save and compared with a pure-Python
haversine calculation) and a thin wrapper around Django's email backend so
every notification goes through one place, per Coding Plan §5 and §11.
"""
import math

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def geocode_address(address):
    """One-time free geocode on address save, using OpenStreetMap's free
    Nominatim API (no API key, rate-limited to 1 req/sec — acceptable at
    portfolio scale). Returns (lat, lng) or (None, None) on any failure so
    a flaky network never blocks a profile/location save."""
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": address, "format": "json", "limit": 1},
            headers={"User-Agent": "ShiftFloor/1.0 (portfolio project)"},
            timeout=5,
        )
        resp.raise_for_status()
        results = resp.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception:
        pass
    return None, None


def haversine_miles(lat1, lng1, lat2, lng2):
    """Great-circle distance in miles between two lat/lng points.
    Free — no third-party distance-matrix API required."""
    if None in (lat1, lng1, lat2, lng2):
        return None

    r = 3958.8  # Earth radius in miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return r * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def send_notification_email(subject, template_name, context, to_email):
    """Single choke point for all transactional email so notification
    behavior (from-address, template wrapping) stays consistent across
    shifts_app, matching_app, workers_app, etc."""
    if not to_email:
        return
    body = render_to_string(template_name, context)
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=True,
    )
