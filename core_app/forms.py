class NoColonLabelMixin:
    """Drops Django's default trailing ":" on rendered field labels
    (Rubric E.2) so form.as_p() output reads consistently with the rest
    of the site's design system instead of Django's bare scaffolded look.

    A plain `label_suffix = ""` class attribute does NOT work for this —
    BaseForm.__init__ hardcodes `label_suffix if label_suffix is not None
    else _(":")` as the instance value, so it never falls back to a class
    attribute at all; the class-level override is silently ignored unless
    label_suffix is explicitly passed into __init__. This mixin does
    that, so every form using it only needs to list it first in its base
    classes."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)
