from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

load_dotenv(dotenv_path=find_dotenv(), verbose=True)

DEBUG: bool = os.getenv(key="DEBUG", default="True").lower() == "true"
BASE_DIR: Path = Path(__file__).resolve().parent.parent
SECRET_KEY: str = os.getenv("SECRET_KEY", default="")
ADMINS: list[tuple[str, str]] = [("Joakim Hellsén", "django@feedvault.se")]
ALLOWED_HOSTS: list[str] = [".feedvault.se", ".localhost", "127.0.0.1"]
CSRF_COOKIE_DOMAIN = ".feedvault.se"
CSRF_TRUSTED_ORIGINS: list[str] = ["https://feedvault.se", "https://www.feedvault.se"]
TIME_ZONE = "Europe/Stockholm"
USE_TZ = True
USE_I18N = False
LANGUAGE_CODE = "en-us"
DECIMAL_SEPARATOR = ","
THOUSAND_SEPARATOR = " "
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
USE_X_FORWARDED_HOST = True
INTERNAL_IPS: list[str] = ["127.0.0.1", "localhost"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SITE_ID = 1
PASSWORD_HASHERS: list[str] = ["django.contrib.auth.hashers.Argon2PasswordHasher"]
ROOT_URLCONF = "feedvault.urls"
WSGI_APPLICATION = "feedvault.wsgi.application"
NINJA_PAGINATION_PER_PAGE = 1000

# Is True when running tests, used for not spamming Discord when new users are created
TESTING: bool = len(sys.argv) > 1 and sys.argv[1] == "test"

INSTALLED_APPS: list[str] = [
    "feedvault.apps.FeedVaultConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
]

MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
database_folder: Path = BASE_DIR / "data"
database_folder.mkdir(parents=True, exist_ok=True)
DATABASES: dict[str, dict[str, str | Path | bool]] = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": database_folder / "feedvault.sqlite3",
        "ATOMIC_REQUESTS": True,
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
