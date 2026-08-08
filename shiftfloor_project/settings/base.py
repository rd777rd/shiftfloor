"""
Base settings shared by local and production environments.
Environment-specific values are loaded via django-environ from a .env file
(local) or the host platform's environment variables (production/Render).
"""
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)
# Reads a .env file if present (local dev). On Render, real env vars are used.
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="insecure-dev-key-change-me")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "accounts_app",
    "facilities_app",
    "workers_app",
    "shifts_app",
    "matching_app",
    "reviews_app",
    "payments_app",
    "cloudinary_storage",
    "cloudinary",
    "anymail",
    "core_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "shiftfloor_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core_app.context_processors.site_meta",
            ],
        },
    },
]

WSGI_APPLICATION = "shiftfloor_project.wsgi.application"

DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:///" + str(BASE_DIR / "db.sqlite3")),
}

AUTH_USER_MODEL = "accounts_app.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts_app:login"
LOGIN_REDIRECT_URL = "core_app:role_redirect"
LOGOUT_REDIRECT_URL = "core_app:home"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Indiana/Indianapolis"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media (certification documents, profile photos) — Cloudinary free tier.
# Render's free web service disk is ephemeral, so local media storage would
# silently lose files on every redeploy. See Deployment Plan §4.
#
# NOTE (discovered during Step 3 refactor, not in original rubric): this
# used to be set via the standalone STATICFILES_STORAGE / DEFAULT_FILE_STORAGE
# settings, which Django deprecated in 4.2 in favor of the STORAGES dict
# below. Django 5.2 silently ignores the old setting names entirely and
# falls back to its own plain, un-hashed FileSystemStorage for BOTH static
# and media — meaning WhiteNoise's compression/cache-busting was never
# actually active, and worker certification uploads were silently being
# written to Render's ephemeral disk instead of Cloudinary this whole
# time. STORAGES is the only thing Django 5.2 actually reads.
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
CLOUDINARY_STORAGE = {
    "CLOUDINARY_URL": env("CLOUDINARY_URL", default=""),
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Email (Anymail + Brevo free tier, 300/day) ---
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
ANYMAIL = {
    "BREVO_API_KEY": env("ANYMAIL_BREVO_API_KEY", default=""),
}
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@shiftfloor.example.com")

# --- Stripe ---
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="")
STRIPE_CONNECT_CLIENT_ID = env("STRIPE_CONNECT_CLIENT_ID", default="")

# --- Site meta (used by SEO context processor / JSON-LD partials) ---
SITE_NAME = "ShiftFloor"
SITE_DOMAIN = env("SITE_DOMAIN", default="shiftfloor.onrender.com")
SITE_TAGLINE = "Open shifts, filled by lunch."

# Cert types shared across workers_app (certifications) and shifts_app (requirements)
CERTIFICATION_CHOICES = [
    ("FORKLIFT_I", "Forklift — Class I (Electric Motor Rider)"),
    ("FORKLIFT_II", "Forklift — Class II (Electric Motor Narrow Aisle)"),
    ("FORKLIFT_III", "Forklift — Class III (Electric Motor Hand/Rider)"),
    ("FORKLIFT_IV", "Forklift — Class IV (Internal Combustion, Cushion Tire)"),
    ("FORKLIFT_V", "Forklift — Class V (Internal Combustion, Pneumatic Tire)"),
    ("FORKLIFT_VI", "Forklift — Class VI (Electric/IC Tractor)"),
    ("FORKLIFT_VII", "Forklift — Class VII (Rough Terrain)"),
    ("OSHA_10", "OSHA 10-Hour General Industry"),
    ("OSHA_30", "OSHA 30-Hour General Industry"),
    ("GENERAL", "General Labor (no certification required)"),
]
