import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

#ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])
ALLOWED_HOSTS = ['*']

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',
]

LOCAL_APPS = [
    'apps.core',
    'apps.users',
    'apps.products',
    'apps.orders',
    'apps.design_tool',
    'apps.pricing',
    'apps.services',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'drishthi_printing.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'drishthi_printing.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-in'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Login URLs
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@drishthiprinting.com')

# Payment Gateway Configuration
RAZORPAY_KEY_ID = env('RAZORPAY_KEY_ID', default='')
RAZORPAY_KEY_SECRET = env('RAZORPAY_KEY_SECRET', default='')

# Business Configuration
BUSINESS_CONFIG = {
    'COMPANY_NAME': 'Drishthi Printing',
    'COMPANY_ADDRESS': 'Mumbai, India',
    'COMPANY_PHONE': '+91 98765 43210',
    'COMPANY_EMAIL': 'info@drishthiprinting.com',
    'GST_RATE': 0.18,
    'FREE_SHIPPING_THRESHOLD': 1000,
    'RUSH_DELIVERY_MULTIPLIER': 1.2,
}

# Design Tool Configuration
DESIGN_TOOL_CONFIG = {
    'MAX_FILE_SIZE': 10 * 1024 * 1024,  # 10MB
    'ALLOWED_FORMATS': ['jpg', 'jpeg', 'png', 'pdf', 'svg'],
    'CANVAS_MAX_WIDTH': 4000,
    'CANVAS_MAX_HEIGHT': 4000,
    'DEFAULT_DPI': 300,
}

# External API Keys for Design Tool
PIXABAY_API_KEY = '52058938-73b864e28b7dc377c6a8fce66'
UNSPLASH_ACCESS_KEY = env('UNSPLASH_ACCESS_KEY', default='')
PEXELS_API_KEY = env('PEXELS_API_KEY', default='')

# Celery Configuration (for background tasks)
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/0')

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://127.0.0.1:6379/1'),
    }
}

# Security Settings for Production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True



FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Template upload directory
TEMPLATE_UPLOAD_DIR = 'templates/uploads/'

# Allowed file extensions for templates
ALLOWED_TEMPLATE_EXTENSIONS = ['svg', 'json']

# SVG Processing Settings
SVG_TO_CANVAS_SCALE = 3.78

# Free Image API Keys for Design Tool
# Get these free API keys from:
# - Unsplash: https://unsplash.com/developers
# - Pixabay: https://pixabay.com/accounts/register/
# - Pexels: https://www.pexels.com/api/

UNSPLASH_ACCESS_KEY = env('UNSPLASH_ACCESS_KEY', default='')
PIXABAY_API_KEY = env('PIXABAY_API_KEY', default='')
PEXELS_API_KEY = env('PEXELS_API_KEY', default='')

# Design Tool Free Image API Configuration
FREE_IMAGE_APIS = {
    'unsplash': {
        'enabled': bool(UNSPLASH_ACCESS_KEY),
        'rate_limit_per_hour': 50,
        'api_url': 'https://api.unsplash.com',
        'attribution_required': True,
    },
    'pixabay': {
        'enabled': bool(PIXABAY_API_KEY),
        'rate_limit_per_hour': 5000,
        'api_url': 'https://pixabay.com/api',
        'attribution_required': False,
    },
    'pexels': {
        'enabled': bool(PEXELS_API_KEY),
        'rate_limit_per_hour': 200,
        'api_url': 'https://api.pexels.com/v1',
        'attribution_required': True,
    },
}