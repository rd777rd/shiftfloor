"""
Shared structured-data templatetags. Kept in core_app and reused via
{% include %} across apps rather than duplicated per template, per Coding
Plan §7 and Rubric D.32. JobPosting schema lives in shifts_app since it's
tightly coupled to the Shift model, but Organization/Breadcrumb/FAQ are
generic enough to live here.
"""
import json

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag("partials/_organization_jsonld.html", takes_context=True)
def organization_jsonld(context):
    request = context["request"]
    domain = f"https://{settings.SITE_DOMAIN}"
    data = {
        "@context": "https://schema.org",
        "@type": "EmploymentAgency",
        "name": settings.SITE_NAME,
        "url": domain,
        "description": (
            "ShiftFloor connects Indianapolis-area warehouse and "
            "distribution facilities with pre-vetted, certified workers "
            "for short-notice shift coverage."
        ),
        "areaServed": {
            "@type": "City",
            "name": "Indianapolis",
        },
    }
    return {"json_ld": mark_safe(json.dumps(data))}


@register.simple_tag
def breadcrumb_jsonld(*crumbs):
    """Usage: {% breadcrumb_jsonld "Home:/" "Shifts:/shifts/browse/" %}
    Each crumb is 'Label:URL'."""
    items = []
    for i, crumb in enumerate(crumbs, start=1):
        label, url = crumb.split(":", 1)
        items.append(
            {
                "@type": "ListItem",
                "position": i,
                "name": label,
                "item": f"https://{settings.SITE_DOMAIN}{url}",
            }
        )
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }
    return mark_safe(
        f'<script type="application/ld+json">{json.dumps(data)}</script>'
    )


@register.simple_tag
def faq_jsonld(qa_pairs):
    """qa_pairs: list of (question, answer) tuples."""
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in qa_pairs
        ],
    }
    return mark_safe(
        f'<script type="application/ld+json">{json.dumps(data)}</script>'
    )
