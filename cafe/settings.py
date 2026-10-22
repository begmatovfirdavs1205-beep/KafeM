import os
import secrets
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# Read a local .env file without requiring a separate package. Environment variables
# already defined by the operating system always take precedence.
env_file = BASE_DIR / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))

# Use a project-specific variable so a generic DEBUG variable inherited from a
# developer tool or hosting environment cannot accidentally break local startup.
DEBUG = os.environ.get("CAFE_DEBUG", "True").lower() in {"1", "true", "yes"}
SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY and DEBUG:
    SECRET_KEY = secrets.token_urlsafe(48)
if not DEBUG and (not SECRET_KEY or SECRET_KEY == "replace-this-for-production"):
    raise ImproperlyConfigured("Set a unique SECRET_KEY in .env before running with DEBUG=False.")
ALLOWED_HOSTS = [host.strip() for host in os.environ.get("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if host.strip()]

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "menu",
    "orders",
]

JAZZMIN_SETTINGS = {
    "site_title": "Моё Кафе — Администрирование",
    "site_header": "Моё Кафе",
    "site_brand": "Моё Кафе",
    "welcome_sign": "Панель управления кафе",
    "copyright": "Моё Кафе · Душанбе",
    "search_model": ["menu.Product", "orders.Order"],
    "topmenu_links": [{"name": "Открыть сайт", "url": "/", "new_window": True}],
    "order_with_respect_to": ["orders.order", "menu.category", "menu.product", "auth.user"],
    "icons": {
        "menu": "fas fa-book-open",
        "menu.category": "fas fa-layer-group",
        "menu.product": "fas fa-utensils",
        "orders": "fas fa-clipboard-list",
        "orders.order": "fas fa-receipt",
        "orders.orderitem": "fas fa-list-ul",
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    "default_icon_parents": "fas fa-folder-open",
    "default_icon_children": "fas fa-circle",
    "show_ui_builder": False,
    "show_theme_chooser": False,
    "language_chooser": False,
    "changeform_format": "horizontal_tabs",
    "custom_css": "css/jazzmin.css",
}

JAZZMIN_UI_TWEAKS = {
    "theme": "sandstone",
    "default_theme_mode": "light",
    "navbar": "navbar-dark",
    "sidebar": "sidebar-dark-primary",
    "accent": "accent-warning",
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cafe.urls"
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
                "core.context_processors.cart_summary",
            ],
        },
    },
]

WSGI_APPLICATION = "cafe.wsgi.application"
ASGI_APPLICATION = "cafe.asgi.application"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru"
LANGUAGES = [("ru", "Русский")]
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/admin/login/"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
