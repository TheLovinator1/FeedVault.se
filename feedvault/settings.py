from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

load_dotenv(dotenv_path=find_dotenv(), verbose=True)
TESTING: bool = len(sys.argv) > 1 and sys.argv[1] == "test"

BASE_DIR: Path = Path(__file__).resolve().parent.parent

DEBUG: bool = os.getenv(key="DEBUG", default="True").lower() == "true"
SECRET_KEY: str = os.getenv("SECRET_KEY", default="")

TIME_ZONE = "Europe/Stockholm"
LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_TZ = True

ADMINS: list[tuple[str, str]] = [("Joakim Hellsén", "tlovinator@gmail.com")]
ALLOWED_HOSTS: list[str] = [".feedvault.se", ".localhost", "127.0.0.1"]
USE_X_FORWARDED_HOST = True
INTERNAL_IPS: list[str] = ["127.0.0.1", "localhost", "192.168.1.143"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
WSGI_APPLICATION = "feedvault.wsgi.application"
ROOT_URLCONF = "feedvault.urls"
SITE_ID = 1

if not DEBUG:
    CSRF_COOKIE_DOMAIN = ".feedvault.se"
    CSRF_TRUSTED_ORIGINS: list[str] = ["https://feedvault.se", "https://www.feedvault.se"]

TIME_ZONE = "Europe/Stockholm"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER: str = os.getenv(key="EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD: str = os.getenv(key="EMAIL_HOST_PASSWORD", default="")
EMAIL_SUBJECT_PREFIX = "[FeedVault] "
EMAIL_USE_LOCALTIME = True
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL: str = os.getenv(key="EMAIL_HOST_USER", default="webmaster@localhost")
SERVER_EMAIL: str = os.getenv(key="EMAIL_HOST_USER", default="webmaster@localhost")


STATIC_URL = "static/"
STATIC_ROOT: Path = BASE_DIR / "staticfiles"
STATIC_ROOT.mkdir(parents=True, exist_ok=True)
STATICFILES_DIRS: list[Path] = [BASE_DIR / "static"]
for static_dir in STATICFILES_DIRS:
    static_dir.mkdir(parents=True, exist_ok=True)


MEDIA_URL = "media/"
MEDIA_ROOT: Path = BASE_DIR / "media"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)


INSTALLED_APPS: list[str] = [
    "feeds.apps.FeedsConfig",
    "debug_toolbar",
    "django.contrib.auth",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "django_htmx",
]

MIDDLEWARE: list[str] = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

# TODO(TheLovinator): #1 Use unix socket for postgres in production
# https://github.com/TheLovinator1/feedvault.se/issues/1
DATABASES: dict[str, dict[str, str]] = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", ""),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", ""),
    },
}

if not DEBUG:
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS: str = "default"

# TODO(TheLovinator): #2 Use unix socket for redis in production
# https://github.com/TheLovinator1/feedvault.se/issues/2
REDIS_LOCATION: str = f"redis://{os.getenv('REDIS_HOST', "")}:{os.getenv('REDIS_PORT', "")}/1"
CACHES: dict[str, dict[str, str | dict[str, str]]] = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_LOCATION,
        "KEY_PREFIX": "feedvault-dev" if DEBUG else "feedvault",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PARSER_CLASS": "redis.connection._HiredisParser",
            "PASSWORD": os.getenv("REDIS_PASSWORD", ""),
        },
    },
}

# A list containing the settings for all template engines to be used with Django.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "feedvault.context_processors.add_global_context",
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                ),
            ],
        },
    },
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.utils.autoreload": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

STORAGES: dict[str, dict[str, str]] = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        if TESTING
        else "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
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
