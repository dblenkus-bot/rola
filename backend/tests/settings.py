"""
Django settings for running tests for rolca-core package.

"""

import os

import django
from django.utils.translation import gettext_lazy as _

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = "secret"

DEBUG = False
USE_TZ = True
TIME_ZONE = "UTC"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
AUTH_USER_MODEL = "auth.User"

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]


INSTALLED_APPS = (
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django_filters",
    "rest_framework",
    "rolca.backup",
    "rolca.core",
    "rolca.payment",
    "rolca.rating",
)

ROOT_URLCONF = "tests.urls"

LOGIN_REDIRECT_URL = "/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(PROJECT_ROOT, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

LANGUAGES = (
    ("en", _("English")),
    ("sl", _("Slovene")),
)

LANGUAGE_CODE = "en"

LOCALE_PATHS = (os.path.join(PROJECT_ROOT, "locale"),)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("ROLCA_POSTGRESQL_NAME", "rolca"),
        "USER": os.environ.get("ROLCA_POSTGRESQL_USER", "rolca"),
        "PASSWORD": os.environ.get("ROLCA_POSTGRESQL_PASSWORD", ""),
        "HOST": os.environ.get("ROLCA_POSTGRESQL_HOST", "localhost"),
        "PORT": int(os.environ.get("ROLCA_POSTGRESQL_PORT", 5432)),
    }
}

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.backends.DjangoFilterBackend",
    ),
}

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

ASGI_APPLICATION = "tests.routing.application"

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media")
MEDIA_URL = "/media/"
STATIC_URL = "/static/"

ROLCA_MAX_UPLOAD_SIZE = 1048576
ROLCA_MAX_UPLOAD_RESOLUTION = 2400
ROLCA_ACCEPTED_FORMATS = ["JPEG"]

if django.VERSION >= (6, 1):
    MAILERS = {"default": {"BACKEND": "django.core.mail.backends.locmem.EmailBackend"}}
else:
    EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
BACKUP_AWS_BUCKET_NAME = "test-backups"
BACKUP_AWS_ACCESS_KEY_ID = "test-access-key"
BACKUP_AWS_SECRET_ACCESS_KEY = "test-secret-key"
