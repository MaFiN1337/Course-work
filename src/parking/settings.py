from pathlib import Path

from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('DJANGO_SECRET_KEY')

DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1", cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    "rest_framework",
    "drf_spectacular",
    "rest_framework_simplejwt",
    "corsheaders",
    
    'src.api',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware", 
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'src.parking.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'src.parking.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Kyiv'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        'rest_framework.permissions.IsAuthenticated',
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Smart Parking API",
    "DESCRIPTION": "Search lots/spots, book & cancel.",
    "VERSION": "0.1.0",
}

from datetime import timedelta
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
}

CORS_ALLOW_ALL_ORIGINS = True 

STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}
}

USING_POSTGRES = config('USING_POSTGRES', default=False, cast=bool)
SQLITE_MODIFIED = config('SQLITE_MODIFIED', default=True, cast=bool) 

try:
    if config("PG_DB_NAME", default=None) and USING_POSTGRES:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": config("PG_DB_NAME"),
                "USER": config("PG_USERNAME"),
                "PASSWORD": config("PG_PASSWORD"),
                "HOST": config("PG_HOSTNAME"),
                "PORT": config("PG_PORT", "5432"),
                "OPTIONS": {
                    "connect_timeout": 10,
                    "options": "-c statement_timeout=30000"
                },
                "CONN_MAX_AGE": 60,
            }
        }
    else:
        if SQLITE_MODIFIED:
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': BASE_DIR / f'db_mod.sqlite3',
                    'OPTIONS': {
                        'init_command': (
                            'PRAGMA journal_mode=WAL; '
                            'PRAGMA synchronous=NORMAL; '
                            'PRAGMA cache_size=-64000; '  
                            'PRAGMA mmap_size=268435456; '
                            'PRAGMA temp_store=MEMORY;'
                        ),
                        'transaction_mode': 'IMMEDIATE',
                        'timeout': 20,
                    }
                }
            }
        else:
           DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': BASE_DIR / f'db_def.sqlite3',
                    'OPTIONS': {
                        'init_command': (
                            'PRAGMA journal_mode=DELETE; '
                            'PRAGMA synchronous=FULL; '
                            'PRAGMA cache_size=-2000; '
                            'PRAGMA mmap_size=0; '   
                            'PRAGMA temp_store=DEFAULT;'
                        ),
                        'timeout': 5,
                    }
                }
            }
except NameError:
    pass

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="sk-test...")
STRIPE_PUBLIC_KEY = config("STRIPE_PUBLIC_KEY", default="pk-test...")
STRIPE_CURRENCY = config("STRIPE_CURRENCY", default="usd")
 