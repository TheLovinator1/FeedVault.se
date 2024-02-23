from __future__ import annotations

import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

load_dotenv(dotenv_path=find_dotenv(), verbose=True)


# Run Django in debug mode
DEBUG: bool = os.getenv(key="DEBUG", default="True").lower() == "true"

BASE_DIR: Path = Path(__file__).resolve().parent.parent

# The secret key is used for cryptographic signing, and should be set to a unique, unpredictable value.
SECRET_KEY: str = os.getenv("SECRET_KEY", default="")

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "feeds.apps.FeedsConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "feedvault.urls"

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

WSGI_APPLICATION = "feedvault.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES: dict[str, dict[str, str]] = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "feedvault",
        "USER": os.getenv(key="POSTGRES_USER", default=""),
        "PASSWORD": os.getenv(key="POSTGRES_PASSWORD", default=""),
        "HOST": os.getenv(key="POSTGRES_HOST", default=""),
        "PORT": os.getenv(key="POSTGRES_PORT", default="5432"),
    },
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

# A list of all the people who get code error notifications. When DEBUG=False and a view raises an exception, Django
ADMINS: list[tuple[str, str]] = [("Joakim Hellsén", "django@feedvault.se")]

# A list of strings representing the host/domain names that this Django site can serve.
# .feedvault.se will match *.feedvault.se and feedvault.se
ALLOWED_HOSTS: list[str] = [".feedvault.se", ".localhost", "127.0.0.1"]

# The time zone that Django will use to display datetimes in templates and to interpret datetimes entered in forms
TIME_ZONE = "Europe/Stockholm"

# If datetimes will be timezone-aware by default. If True, Django will use timezone-aware datetimes internally.
USE_TZ = True

# Don't use Django's translation system
USE_I18N = False

# Decides which translation is served to all users.
LANGUAGE_CODE = "en-us"

# Default decimal separator used when formatting decimal numbers.
DECIMAL_SEPARATOR = ","

# Use a space as the thousand separator instead of a comma
THOUSAND_SEPARATOR = " "

# Use gmail for sending emails
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER: str = os.getenv(key="EMAIL_HOST_USER", default="webmaster@localhost")
EMAIL_HOST_PASSWORD: str = os.getenv(key="EMAIL_HOST_PASSWORD", default="")
EMAIL_SUBJECT_PREFIX = "[FeedVault] "
EMAIL_USE_LOCALTIME = True
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL: str = os.getenv(key="EMAIL_HOST_USER", default="webmaster@localhost")
SERVER_EMAIL: str = os.getenv(key="EMAIL_HOST_USER", default="webmaster@localhost")

# Use the X-Forwarded-Host header
USE_X_FORWARDED_HOST = True

# Set the Referrer Policy HTTP header on all responses that do not already have one.
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Internal IPs that are allowed to see debug views
INTERNAL_IPS: list[str] = ["127.0.0.1", "localhost"]

STATIC_URL = "static/"
STATIC_ROOT: Path = BASE_DIR / "staticfiles"
STATICFILES_DIRS: list[Path] = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Our site ID
SITE_ID = 1

PASSWORD_HASHERS: list[str] = ["django.contrib.auth.hashers.Argon2PasswordHasher"]
