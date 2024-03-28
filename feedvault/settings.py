from __future__ import annotations

import os
import sys
from pathlib import Path

from django.utils import timezone
from dotenv import find_dotenv, load_dotenv

load_dotenv(dotenv_path=find_dotenv(), verbose=True)

# Is True when running tests, used for not spamming Discord when new users are created
TESTING: bool = len(sys.argv) > 1 and sys.argv[1] == "test"

DEBUG: bool = os.getenv(key="DEBUG", default="True").lower() == "true"
BASE_DIR: Path = Path(__file__).resolve().parent.parent
SECRET_KEY: str = os.getenv("SECRET_KEY", default="")
ADMINS: list[tuple[str, str]] = [("Joakim Hellsén", "django@feedvault.se")]

ALLOWED_HOSTS: list[str] = [".feedvault.se", ".localhost", "127.0.0.1"]

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

USE_X_FORWARDED_HOST = True
INTERNAL_IPS: list[str] = ["127.0.0.1", "localhost", "192.168.1.143"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SITE_ID = 1

# https://docs.djangoproject.com/en/5.0/topics/auth/passwords/#using-argon2-with-django
PASSWORD_HASHERS: list[str] = ["django.contrib.auth.hashers.Argon2PasswordHasher"]
ROOT_URLCONF = "feedvault.urls"

STATIC_URL = "static/"
STATIC_ROOT: Path = BASE_DIR / "staticfiles"
STATIC_ROOT.mkdir(parents=True, exist_ok=True)
STATICFILES_DIRS: list[Path] = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT: Path = BASE_DIR / "media"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)


INSTALLED_APPS: list[str] = [
    "feedvault.apps.FeedVaultConfig",
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

DATABASE_PATH: str = os.getenv("DATABASE_PATH", "/data")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path(DATABASE_PATH) / "feedvault.sqlite3",
        "OPTIONS": {
            "timeout": 30,
        },
    },
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
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


# Create data/logs folder if it doesn't exist
log_folder: Path = BASE_DIR / "data" / "logs"
log_folder.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "data" / "logs" / f"{timezone.now().strftime('%Y%m%d')}.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "django.utils.autoreload": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "": {
            "handlers": ["console", "file"],
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
