"""Covers Rubric E.1 (self-hosted font references must not point at
missing files) and E.2 (transactional forms must not render Django's raw
colon-suffixed labels, and should sit inside the site's .card treatment)."""
import re
from pathlib import Path

import pytest
from django.test import Client
from django.urls import reverse


def test_base_css_has_no_dangling_font_face_references():
    css_path = Path(__file__).resolve().parent.parent.parent / "static" / "css" / "base.css"
    css_text = css_path.read_text()
    # Strip comments before checking — the fix's own explanatory comment
    # legitimately names the removed files in prose, which shouldn't be
    # mistaken for an actual reference still in effect.
    code_only = re.sub(r"/\*.*?\*/", "", css_text, flags=re.DOTALL)
    assert "@font-face" not in code_only
    assert ".woff2" not in code_only


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name", ["accounts_app:signup_worker", "accounts_app:signup_facility", "accounts_app:login"]
)
def test_form_pages_have_no_raw_colon_labels_and_use_card_wrapper(url_name):
    client = Client()
    response = client.get(reverse(url_name))
    content = response.content.decode()
    # Django's default label_suffix renders e.g. "Username:</label>" —
    # confirming that pattern is gone (not just that *a* colon is absent,
    # since e.g. "Get started" text nearby has none anyway).
    assert ":</label>" not in content
    assert 'class="card"' in content
