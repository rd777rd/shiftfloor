from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.templatetags.static import static as static_url
from django.urls import path, include
from django.views.generic import TemplateView

from .sitemaps import sitemaps

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core_app.urls")),
    path("accounts/", include("accounts_app.urls")),
    path("facilities/", include("facilities_app.urls")),
    path("workers/", include("workers_app.urls")),
    path("shifts/", include("shifts_app.urls")),
    path("matching/", include("matching_app.urls")),
    path("reviews/", include("reviews_app.urls")),
    path("payments/", include("payments_app.urls")),
    # SEO: sitemap + robots.txt, per SEO Plan §6
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots_txt",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
