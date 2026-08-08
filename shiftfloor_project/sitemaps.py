from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from shifts_app.models import Shift
from facilities_app.models import Facility


class StaticViewSitemap(Sitemap):
    """Marketing/static pages — kept out of the app-level sitemaps since
    they don't belong to any single model."""

    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return [
            "core_app:home",
            "core_app:how_it_works",
            "core_app:certifications_info",
            "core_app:pricing",
            "core_app:faq",
            "core_app:contact",
        ]

    def location(self, item):
        return reverse(item)


class ShiftSitemap(Sitemap):
    """Only OPEN shifts are indexable — expired/filled/cancelled shifts are
    excluded so crawl budget isn't wasted on stale JobPosting content and
    Google never sees a dead listing. See SEO Plan §6 and Rubric B.12."""

    changefreq = "hourly"
    priority = 0.9

    def items(self):
        return Shift.objects.filter(status="OPEN")

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse("shifts_app:shift_detail", args=[obj.slug])


class FacilitySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Facility.objects.filter(verified=True)

    def location(self, obj):
        return reverse("facilities_app:facility_detail", args=[obj.slug])


sitemaps = {
    "static": StaticViewSitemap,
    "shifts": ShiftSitemap,
    "facilities": FacilitySitemap,
}
