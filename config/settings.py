import logging
import os
import sys
from pathlib import Path
from typing import Any

import sentry_sdk
from dotenv import load_dotenv
from platformdirs import user_data_dir

logger: logging.Logger = logging.getLogger("feedvault.settings")

load_dotenv(verbose=True)

TRUE_VALUES: set[str] = {"1", "true", "yes", "y", "on"}


def env_bool(key: str, *, default: bool = False) -> bool:
    """Read a boolean from the environment, accepting common truthy values.

    Returns:
        bool: Parsed boolean value or the provided default when unset.
    """
    value: str | None = os.getenv(key)
    if value is None:
        return default
    return value.strip().lower() in TRUE_VALUES


def env_int(key: str, default: int) -> int:
    """Read an integer from the environment with a fallback default.

    Returns:
        int: Parsed integer value or the provided default when unset.
    """
    value: str | None = os.getenv(key)
    return int(value) if value is not None else default


DEBUG: bool = env_bool(key="DEBUG", default=True)
TESTING: bool = (
    env_bool(key="TESTING", default=False)
    or "test" in sys.argv
    or "PYTEST_VERSION" in os.environ
)


def get_data_dir() -> Path:
    r"""Get the directory where the application data will be stored.

    This directory is created if it does not exist.

    Returns:
        Path: The directory where the application data will be stored.

            For example, on Windows, it might be:
            `C:\Users\lovinator\AppData\Roaming\TheLovinator\FeedVault`

            In this directory, application data such as media and static files will be stored.
    """
    data_dir: str = user_data_dir(
        appname="FeedVault",
        appauthor="TheLovinator",
        roaming=True,
        ensure_exists=True,
    )
    return Path(data_dir)


DATA_DIR: Path = get_data_dir()

ADMINS: list[tuple[str, str]] = [("Joakim Hellsén", "tlovinator@gmail.com")]
BASE_DIR: Path = Path(__file__).resolve().parent.parent
ROOT_URLCONF = "config.urls"
SECRET_KEY: str = os.getenv("DJANGO_SECRET_KEY", default="")
if not SECRET_KEY:
    logger.error("DJANGO_SECRET_KEY environment variable is not set.")
    sys.exit(1)

DEFAULT_FROM_EMAIL: str | None = os.getenv(key="EMAIL_HOST_USER", default=None)
EMAIL_HOST: str = os.getenv(key="EMAIL_HOST", default="smtp.gmail.com")
EMAIL_HOST_PASSWORD: str | None = os.getenv(key="EMAIL_HOST_PASSWORD", default=None)
EMAIL_HOST_USER: str | None = os.getenv(key="EMAIL_HOST_USER", default=None)
EMAIL_PORT: int = env_int(key="EMAIL_PORT", default=587)
EMAIL_SUBJECT_PREFIX = "[FeedVault] "
EMAIL_TIMEOUT: int = env_int(key="EMAIL_TIMEOUT", default=10)
EMAIL_USE_LOCALTIME = True
EMAIL_USE_TLS: bool = env_bool(key="EMAIL_USE_TLS", default=True)
EMAIL_USE_SSL: bool = env_bool(key="EMAIL_USE_SSL", default=False)
SERVER_EMAIL: str | None = os.getenv(key="EMAIL_HOST_USER", default=None)

LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/accounts/login/"
LOGOUT_REDIRECT_URL = "/"

ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_EMAIL_REQUIRED = False

MEDIA_ROOT: Path = DATA_DIR / "media"
MEDIA_ROOT.mkdir(exist_ok=True)
MEDIA_URL = "/media/"

STATIC_ROOT: Path = DATA_DIR / "staticfiles"
STATIC_ROOT.mkdir(exist_ok=True)
STATIC_URL = "/static/"
STATICFILES_DIRS: list[Path] = [BASE_DIR / "static"]

TIME_ZONE = "UTC"
WSGI_APPLICATION = "config.wsgi.application"

INTERNAL_IPS: list[str] = []
if DEBUG:
    INTERNAL_IPS = ["127.0.0.1", "localhost"]  # pyright: ignore[reportConstantRedefinition]

ALLOWED_HOSTS: list[str] = [".localhost", "127.0.0.1", "[::1]", "testserver"]
if not DEBUG:
    ALLOWED_HOSTS = ["feedvault.se"]  # pyright: ignore[reportConstantRedefinition]

LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"level": "DEBUG", "class": "logging.StreamHandler"}},
    "loggers": {
        "": {"handlers": ["console"], "level": "INFO", "propagate": True},
        "feedvault": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.utils.autoreload": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

INSTALLED_APPS: list[str] = [
    # Django built-in apps
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    # Internal apps
    # Third-party apps
    "django_celery_results",
    "django_celery_beat",
]

MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]


TEMPLATES: list[dict[str, Any]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
            ],
        },
    },
]

DATABASES: dict[str, dict[str, Any]] = (
    {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
    if TESTING
    else {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "feedvault"),
            "USER": os.getenv("POSTGRES_USER", "feedvault"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": env_int("POSTGRES_PORT", 5432),
            "CONN_MAX_AGE": env_int("CONN_MAX_AGE", 60),
            "CONN_HEALTH_CHECKS": env_bool("CONN_HEALTH_CHECKS", default=True),
            "OPTIONS": {"connect_timeout": env_int("DB_CONNECT_TIMEOUT", 10)},
        },
    }
)

if not TESTING:
    INSTALLED_APPS = [*INSTALLED_APPS, "debug_toolbar", "silk"]  # pyright: ignore[reportConstantRedefinition]
    MIDDLEWARE = [  # pyright: ignore[reportConstantRedefinition]
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "silk.middleware.SilkyMiddleware",
        *MIDDLEWARE,
    ]

    if not DEBUG:
        sentry_sdk.init(
            dsn="https://1aa1ac672090fb795783de0e90a2b19f@o4505228040339456.ingest.us.sentry.io/4511055670738944",
            send_default_pii=True,
            enable_logs=True,
            traces_sample_rate=1.0,
            profile_session_sample_rate=1.0,
            profile_lifecycle="trace",
        )

REDIS_URL_CACHE: str = os.getenv(
    key="REDIS_URL_CACHE",
    default="redis://localhost:6379/0",
)
REDIS_URL_CELERY: str = os.getenv(
    key="REDIS_URL_CELERY",
    default="redis://localhost:6379/1",
)

CACHES: dict[str, dict[str, str]] = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL_CACHE,
    },
}

CELERY_BROKER_URL: str = REDIS_URL_CELERY
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
