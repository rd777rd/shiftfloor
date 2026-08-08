from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Local dev/test never runs `collectstatic`, so the manifest-backed
# staticfiles storage from base.py (which requires staticfiles.json to
# exist — see the STORAGES note there) doesn't apply here: it would raise
# "Missing staticfiles manifest entry" on every {% static %} tag the
# moment a new asset (like img/og-default.png) is added without a manifest
# rebuild. Local dev gets Django's plain, unhashed static storage instead;
# production keeps the real WhiteNoise compressed/manifest storage, where
# `collectstatic` genuinely does run as part of the Render build step.
STORAGES = {**STORAGES, "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}}

# Local dev never needs Cloudinary configured — fall back to local disk so
# `runserver` works out of the box without any third-party credentials.
if not env("CLOUDINARY_URL", default=""):
    STORAGES = {**STORAGES, "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"}}
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
