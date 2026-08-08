from django.conf import settings


def site_meta(request):
    """Makes site-wide branding/SEO constants available in every template
    without importing settings directly in each view."""
    return {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_DOMAIN": settings.SITE_DOMAIN,
        "SITE_TAGLINE": settings.SITE_TAGLINE,
    }
