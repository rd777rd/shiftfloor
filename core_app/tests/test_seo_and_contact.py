"""Covers Rubric D.1 (canonical tag), D.2 (og:image/twitter:image), and
F.1 (contact page must show a real, reachable support address)."""
import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name", ["core_app:home", "core_app:how_it_works", "core_app:faq", "core_app:contact"]
)
def test_canonical_tag_present_and_self_referencing(url_name):
    client = Client()
    response = client.get(reverse(url_name))
    content = response.content.decode()
    expected_path = reverse(url_name)
    assert 'rel="canonical"' in content
    assert f'href="https://shiftfloor.onrender.com{expected_path}"' in content


@pytest.mark.django_db
def test_og_and_twitter_image_present():
    client = Client()
    response = client.get(reverse("core_app:home"))
    content = response.content.decode()
    assert 'property="og:image"' in content
    assert 'name="twitter:image"' in content
    assert "og-default.png" in content


@pytest.mark.django_db
def test_contact_page_shows_real_support_address():
    client = Client()
    response = client.get(reverse("core_app:contact"))
    content = response.content.decode()
    assert "shiftfloorllc@gmail.com" in content
    assert "mailto:shiftfloorllc@gmail.com" in content
    assert "example.com" not in content
