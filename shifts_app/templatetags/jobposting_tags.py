import json

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def jobposting_jsonld(shift):
    """Only renders for shifts still eligible (Shift.is_job_posting_eligible)
    — an expired/filled shift emits nothing rather than stale data, per SEO
    Plan §4 and Rubric B.10/B.11."""
    if not shift.is_job_posting_eligible:
        return ""

    location = shift.location
    data = {
        "@context": "https://schema.org/",
        "@type": "JobPosting",
        "title": shift.get_role_type_display(),
        "description": (
            f"{shift.get_role_type_display()} shift at "
            f"{location.facility.name} ({location.label}). "
            f"{'Requires ' + shift.get_required_cert_display() + '.' if shift.required_cert != 'GENERAL' else 'No certification required.'}"
        ),
        "datePosted": shift.created_at.date().isoformat(),
        "validThrough": shift.start_datetime.isoformat(),
        "employmentType": "TEMPORARY",
        "hiringOrganization": {
            "@type": "Organization",
            "name": location.facility.name,
        },
        "jobLocation": {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": location.address,
                "addressLocality": "Indianapolis",
                "addressRegion": "IN",
                "addressCountry": "US",
            },
        },
        "baseSalary": {
            "@type": "MonetaryAmount",
            "currency": "USD",
            "value": {
                "@type": "QuantitativeValue",
                "value": float(shift.pay_rate),
                "unitText": "HOUR",
            },
        },
    }
    return mark_safe(
        f'<script type="application/ld+json">{json.dumps(data)}</script>'
    )
