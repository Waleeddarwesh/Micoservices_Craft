import os
import sys
from pathlib import Path
import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# Add craft-common to path for local dev
sys.path.insert(0, str(BASE_DIR.parent.parent / 'shared' / 'craft-common'))

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

ENVIRONMENT = env('ENVIRONMENT', default='development')
SECRET_KEY = env('SECRET_KEY', default='django-insecure-catalog-service')
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

INSTALLED_APPS = [
    'django_prometheus',
    'admin_interface',
    'colorfield',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    
    'drf_spectacular',
    'corsheaders',
    'django_filters',
    'modeltranslation',
    
    'accounts',
    'products',
    'course',
    'internal',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'craft_common.middleware.request_id.RequestIDMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'catalog_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'catalog_service.wsgi.application'

if env('DATABASE_URL', default=None):
    DATABASES = {
        'default': env.db('DATABASE_URL')
    }
    DATABASES['default']['OPTIONS'] = {'options': '-c search_path=catalog_service,public'}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / 'db.sqlite3'),
        }
    }

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

SPECTACULAR_SETTINGS = {
    'TITLE': 'Craft API',
    'DESCRIPTION': 'API documentation for Craft application',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True
RABBITMQ_URL = env('RABBITMQ_URL', default='amqp://guest:guest@localhost:5672/')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'craft_common.auth.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'request_id': {
            '()': 'craft_common.logging.structured_logger.RequestIDFilter',
        },
    },
    'formatters': {
        'json': {
            '()': 'craft_common.logging.structured_logger.JsonFormatter',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'filters': ['request_id'],
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

AUTH_USER_MODEL = 'accounts.User'

import os
JWT_PUBLIC_KEY = env('JWT_PUBLIC_KEY', default='').replace('\\n', '\n')


SPECTACULAR_SETTINGS = {
    'TITLE': 'Craft API',
    'DESCRIPTION': 'API documentation for Craft application',
    'VERSION': 'v2.0',
    'TOS': 'https://www.example.com/policies/terms/',
    'CONTACT': {'email': 'Waleeddarwesh2002@gmail.com'},
    'LICENSE': {'name': 'BSD License'},
    'SERVE_INCLUDE_SCHEMA': False,
    'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAuthenticated'],
}

# Celery Settings
CELERY_BROKER_URL = env('RABBITMQ_URL', default='amqp://guest:guest@localhost:5672/')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/0')

# AWS S3 Settings (for video uploads)
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='')
AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL', default=None) # useful for minio/cloudflare R2
VIDEO_UPLOAD_EXPIRATION = env.int('VIDEO_UPLOAD_EXPIRATION', default=3600)
VIDEO_PLAYBACK_EXPIRATION = env.int('VIDEO_PLAYBACK_EXPIRATION', default=14400)
MAX_VIDEO_SIZE_MB = env.int('MAX_VIDEO_SIZE_MB', default=2000)

# Enable django-prometheus DB metrics
if 'default' in DATABASES:
    DATABASES['default']['ENGINE'] = 'django_prometheus.db.backends.postgresql'
