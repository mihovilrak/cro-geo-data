"""
Django settings for django_project project.
"""

import os
import sys
from pathlib import Path
from celery.schedules import crontab
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = BASE_DIR.parent
sys.path.insert(0, str(REPO_ROOT))

load_dotenv(REPO_ROOT / ".env", override=False)

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-this-in-production")

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "rest_framework",
    "rest_framework_gis",
    "django_filters",
    "corsheaders",
    "cadastral",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "django_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "django_project.wsgi.application"

def _env_bool(key: str, default: str = "false") -> bool:
    return os.getenv(key, default).strip().lower() in {"1", "true", "yes"}


if _env_bool("DJANGO_USE_SQLITE", "false"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "NAME": os.getenv("DB_NAME", "postgres"),
            "USER": os.getenv("DB_USER", "postgres"),
            "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
            "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE     = "Europe/Zagreb"
USE_I18N      = True
USE_TZ        = True

STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL   = "/media/"
MEDIA_ROOT  = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
    "DEFAULT_PAGINATION_CLASS": "cadastral.pagination.LargeDatasetPagination",
    "PAGE_SIZE": 100,
    "PAGE_SIZE_QUERY_PARAM": "page_size",
    "MAX_PAGE_SIZE": 1000,
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
}

CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000"
).split(",")
CORS_ALLOW_CREDENTIALS = True

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_CACHE_URL", "redis://redis:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "IGNORE_EXCEPTIONS": True,
        },
        "KEY_PREFIX": "cro_geo",
        "TIMEOUT": 300,
    }
}

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)
CELERY_TASK_DEFAULT_QUEUE = os.getenv("CELERY_TASK_DEFAULT_QUEUE", "cadastral")
CELERY_BEAT_SCHEDULE = {
    "weekly-etl-refresh": {
        "task": "cadastral.tasks.run_full_ingest",
        "schedule": crontab(hour=2, minute=0, day_of_week="0"),
    },
}

GEOSERVER_URL = os.getenv("GEOSERVER_URL", "http://geoserver:8080/geoserver")
GEOSERVER_USER = os.getenv("GEOSERVER_USER", "admin")
GEOSERVER_PASSWORD = os.getenv("GEOSERVER_PASSWORD", "geoserver")
GEOSERVER_WORKSPACE = os.getenv("GEOSERVER_WORKSPACE", "cro-geo-data")
GEOSERVER_DATASTORE = os.getenv("GEOSERVER_DATASTORE", "postgis")

LAYER_CATALOG = [
    {
        "id": "cadastral_parcels",
        "title": "Cadastral Parcels",
        "wms_name": "cadastral_parcels",
        "api_path": "/api/cadastral_parcels/",
        "native_table": "gs.v_cadastral_parcels",
        "workspace": GEOSERVER_WORKSPACE,
        "default": True,
    },
    {
        "id": "cadastral_municipalities",
        "title": "Cadastral Municipalities",
        "wms_name": "cadastral_municipalities",
        "api_path": "/api/cadastral_municipalities/",
        "native_table": "gs.v_cadastral_municipalities",
        "workspace": GEOSERVER_WORKSPACE,
        "default": False,
    },
    {
        "id": "counties",
        "title": "Counties",
        "wms_name": "counties",
        "api_path": "/api/counties/",
        "native_table": "gs.v_counties",
        "workspace": GEOSERVER_WORKSPACE,
        "default": False,
    },
    {
        "id": "municipalities",
        "title": "Municipalities",
        "wms_name": "municipalities",
        "api_path": "/api/municipalities/",
        "native_table": "gs.v_municipalities",
        "workspace": GEOSERVER_WORKSPACE,
        "default": False,
    },
    {
        "id": "settlements",
        "title": "Settlements",
        "wms_name": "settlements",
        "api_path": "/api/settlements/",
        "native_table": "gs.v_settlements",
        "workspace": GEOSERVER_WORKSPACE,
        "default": False,
    },
    {
        "id": "streets",
        "title": "Streets",
        "wms_name": "streets",
        "api_path": "/api/streets/",
        "native_table": "gs.mv_streets",
        "workspace": GEOSERVER_WORKSPACE,
        "default": False,
    },
    {
        "id": "addresses",
        "title": "Addresses",
        "wms_name": "addresses",
        "api_path": "/api/addresses/",
        "native_table": "gs.v_addresses",
        "workspace": GEOSERVER_WORKSPACE,
        "default": False,
    },
]
