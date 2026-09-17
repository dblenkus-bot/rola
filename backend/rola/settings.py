"""Django host configuration from the deployment environment."""

import os
from pathlib import Path
from urllib.parse import quote

from rola.environment import boolean, comma_separated

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = boolean("ROLA_DEBUG")
SECRET_KEY = os.environ["ROLA_SECRET_KEY"]
ALLOWED_HOSTS = comma_separated("ALLOWED_HOSTS")
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
AUTH_USER_MODEL = "drf_user.User"

INSTALLED_APPS = [
    "daphne",
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "rolca.core",
    "rolca.payment",
    "rolca.rating",
    "drf_user.apps.UserConfig",
    "rola_integration",
    "storages",
    "utils",
]
ROLA_BACKUP_ENABLED = boolean("ROLA_BACKUP_ENABLED")
if ROLA_BACKUP_ENABLED:
    INSTALLED_APPS.append("rolca.backup")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "rola.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]
WSGI_APPLICATION = "rola.wsgi.application"
ASGI_APPLICATION = "rola.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("ROLA_POSTGRESQL_NAME", "rola"),
        "USER": os.environ.get("ROLA_POSTGRESQL_USER", "rola"),
        "PASSWORD": os.environ.get("ROLA_POSTGRESQL_PASSWORD", ""),
        "HOST": os.environ.get("ROLA_POSTGRESQL_HOST", "postgresql"),
        "PORT": os.environ.get("ROLA_POSTGRESQL_PORT", "5432"),
        "CONN_MAX_AGE": 0,
        "OPTIONS": {"connect_timeout": 3},
    }
}
if boolean("ROLA_POSTGRESQL_SSLMODE"):
    DATABASES["default"]["OPTIONS"]["sslmode"] = "require"

redis_scheme = "rediss" if boolean("ROLA_REDIS_SSLMODE") else "redis"
redis_password = os.environ.get("ROLA_REDIS_PASSWORD", "")
redis_credentials = f":{quote(redis_password, safe='')}@" if redis_password else ""
redis_host = os.environ.get("ROLA_REDIS_HOST", "redis")
redis_port = os.environ.get("ROLA_REDIS_PORT", "6379")
redis_db = os.environ.get("ROLA_REDIS_DB", "1")
redis_url = os.environ.get(
    "ROLA_REDIS_URL",
    f"{redis_scheme}://{redis_credentials}{redis_host}:{redis_port}/{redis_db}",
)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": redis_url,
        "OPTIONS": {"socket_timeout": 3, "socket_connect_timeout": 3},
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [redis_url]},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
if boolean("ROLA_DISABLE_PASSWORD_VALIDATORS"):
    AUTH_PASSWORD_VALIDATORS = []

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["drf_user.authentication.TokenAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly"
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.backends.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rola.pagination.PageNumberPagination",
    "PAGE_SIZE": 500,
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend"
        if DEBUG
        else "django.core.mail.backends.dummy.EmailBackend"
    }
}
DEFAULT_FROM_EMAIL = os.environ.get("ROLA_DEFAULT_FROM_EMAIL", "webmaster@localhost")
if boolean("ROLA_USE_SES"):
    MAILERS = {
        "default": {
            "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
            "OPTIONS": {
                "host": os.environ.get(
                    "ROLA_SMTP_HOST", "email-smtp.eu-west-1.amazonaws.com"
                ),
                "port": int(os.environ.get("ROLA_SMTP_PORT", "465")),
                "username": os.environ["ROLA_SES_ACCESS_KEY_ID"],
                "password": os.environ["ROLA_SES_SECRET_ACCESS_KEY"],
                "use_ssl": True,
                "timeout": 10,
            },
        }
    }

USE_X_FORWARDED_HOST = boolean("ROLA_USE_X_FORWARDED_HOST")
if boolean("ROLA_TRUST_PROXY"):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = boolean("ROLA_SECURE_SSL_REDIRECT", not DEBUG)
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = int(os.environ.get("ROLA_SECURE_HSTS_SECONDS", "0"))
CSRF_TRUSTED_ORIGINS = comma_separated("ROLA_CSRF_TRUSTED_ORIGINS")

MEDIA_URL = os.environ.get("ROLA_MEDIA_URL", "/media/")
MEDIA_ROOT = Path(os.environ.get("ROLA_MEDIA_ROOT", BASE_DIR / "media"))
STATIC_URL = os.environ.get("ROLA_STATIC_URL", "/static2/")
STATIC_ROOT = Path(os.environ.get("ROLA_STATIC_ROOT", BASE_DIR / "static"))
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
if boolean("ROLA_USE_S3"):
    s3_options = {
        "access_key": os.environ.get("ROLA_AWS_ACCESS_KEY_ID"),
        "secret_key": os.environ.get("ROLA_AWS_SECRET_ACCESS_KEY"),
        "endpoint_url": os.environ.get("ROLA_AWS_S3_ENDPOINT_URL"),
        "region_name": os.environ.get("ROLA_AWS_REGION_NAME"),
        "default_acl": None,
        "object_parameters": {"CacheControl": "max-age=86400"},
    }
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                **s3_options,
                "bucket_name": os.environ["ROLA_AWS_MEDIA_STORAGE_BUCKET_NAME"],
                "file_overwrite": False,
                "querystring_auth": True,
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                **s3_options,
                "bucket_name": os.environ["ROLA_AWS_STATIC_STORAGE_BUCKET_NAME"],
                "querystring_auth": False,
            },
        },
    }

CORS_ALLOWED_ORIGINS = comma_separated("ROLA_CORS_ALLOWED_ORIGINS")
CORS_ALLOWED_ORIGIN_REGEXES = (
    [r"^http://(localhost|127\.0\.0\.1):\d+$"] if DEBUG else []
)
CORS_ALLOW_CREDENTIALS = False
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-disposition",
    "content-type",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
DATA_UPLOAD_MAX_MEMORY_SIZE = 10_485_760
ROLCA_MAX_UPLOAD_SIZE = 5_242_880
ROLCA_MAX_UPLOAD_RESOLUTION = 3500
BACKUP_AWS_BUCKET_NAME = os.environ.get("ROLA_BACKUP_AWS_BUCKET_NAME", "")
BACKUP_AWS_ACCESS_KEY_ID = os.environ.get("ROLA_BACKUP_AWS_ACCESS_KEY_ID", "")
BACKUP_AWS_SECRET_ACCESS_KEY = os.environ.get("ROLA_BACKUP_AWS_SECRET_ACCESS_KEY", "")
DRF_USER_APP_NAME = os.environ.get("ROLA_APP_NAME", "Rola")
ROLA_FRONTEND_URL = os.environ.get("ROLA_FRONTEND_URL", "")
ROLCA_SUBMISSION_CONFIRMATION_CALLBACK = (
    "rola_integration.hooks.send_submission_confirmation"
)
ROLCA_AUTHOR_COUNTRY_CALLBACK = "rola_integration.hooks.get_author_country"
ROLCA_AUTHOR_SELECT_RELATED = ("user__location",)

if boolean("ROLA_LEGACY_MIGRATIONS"):
    from rola_integration.migration_settings import LEGACY_MIGRATION_MODULES

    MIGRATION_MODULES = LEGACY_MIGRATION_MODULES
