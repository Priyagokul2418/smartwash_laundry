from pathlib import Path
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-6csd(vcqi5yp+%tvywn0uwd_0m82g+n2iffq9xss-j0uiyv(q="
)

USE_X_FORWARDED_HOST = True
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ALLOWED_HOSTS = [
    'api.smartwashlaundry.in',
    "smartwashlaundry.in",
    "www.smartwashlaundry.in",
    "reiosglobal.com",
    "www.reiosglobal.com",
    # 'http://localhost:5173',
    # 'http://localhost:8081',
    "127.0.0.1",
    "192.168.1.17",
    "192.168.1.19",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    # "rest_framework_simplejwt.token_blacklist",

    "laundryapp",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",   # FIRST
    "django.middleware.common.CommonMiddleware",

    # "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }



ROOT_URLCONF = "smartwash.urls"
WSGI_APPLICATION = "smartwash.wsgi.application"

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
            ],
        },
    },
]

# =========================
# DATABASE (MySQL)
# =========================
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": os.getenv("DB_NAME", "laundry"),
#         "USER": os.getenv("DB_USER", "smartwash_user"),
#         "PASSWORD": os.getenv("DB_PASSWORD", "smartwash_user"),
#         "HOST": os.getenv("DB_HOST", "127.0.0.1"),
#         "PORT": os.getenv("DB_PORT", "3306"),
#         "OPTIONS": {"init_command": "SET sql_mode='STRICT_TRANS_TABLES'"},
#     }
# }



DEBUG = True
AUTH_USER_MODEL = "laundryapp.User"

# =========================
# STATIC + MEDIA
# =========================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/user_images/"
MEDIA_ROOT = BASE_DIR / "user_images"



# =========================
# CORS / CSRF
# =========================

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = ["https://smartwashlaundry.in"]
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",       # Local frontend
        "http://localhost:5174",
        "http://localhost:8081",
        "http://localhost:19006",
        "http://smartwashlaundry.in",
        "http://www.smartwashlaundry.in",
        "https://smartwashlaundry.in",
        "https://www.smartwashlaundry.in",
    ]

CSRF_TRUSTED_ORIGINS = [
    "https://api.smartwashlaundry.in",
    "https://smartwashlaundry.in",
    "https://www.smartwashlaundry.in",
]

# =========================
# JWT
# =========================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    # "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "user_id",
    "USER_ID_CLAIM": "user_id",
    "CHECK_USER_IS_ACTIVE": False, 
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
