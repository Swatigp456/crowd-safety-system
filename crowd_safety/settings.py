import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-secret-key-here-change-in-production'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Remove 'django.contrib.gis' from here
    # 'django.contrib.gis',  # COMMENT THIS OUT
    
    # Third party apps
    'rest_framework',
    'import_export',
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',
    
    
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    
    # Local apps
    'accounts',
    'monitoring',
    'alerts',
    'dashboard',
    'incidents',
    'api',
    'ai',
    'ml',
    
]

WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": "YOUR_VAPID_PUBLIC_KEY",
    "VAPID_PRIVATE_KEY": "YOUR_VAPID_PRIVATE_KEY",
    "VAPID_ADMIN_EMAIL": "admin@crowdsafety.com"
}

# crowd_safety/settings.py

# WebPush Settings (Test Keys - Replace with your own)
WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": "BCvFp6wXK8xQ9s2dN5m7pL3kR9jH2tY6uW4aE8bQ1cX7zV9nM2pL5kR7jH8tY6uW4aE8bQ1cX7zV",
    "VAPID_PRIVATE_KEY": "E8bQ1cX7zV9nM2pL5kR7jH8tY6uW4aE8bQ1cX7zV9nM2pL5kR7jH8tY6uW4a",
    "VAPID_ADMIN_EMAIL": "admin@crowdsafety.com"
}

# settings.py



BASE_DIR = Path(__file__).resolve().parent.parent

# Admin customization
ADMIN_SITE_HEADER = "Crowd Safety Management System"
ADMIN_SITE_TITLE = "Crowd Safety Admin"
ADMIN_INDEX_TITLE = "Dashboard"

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Ensure static files are served in development
if DEBUG:
    STATICFILES_DIRS = [BASE_DIR / 'static']
else:
    STATIC_ROOT = BASE_DIR / 'staticfiles'
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = False
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'crowd_safety.urls'

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

# Admin customization
ADMIN_SITE_HEADER = "Crowd Safety Management System"
ADMIN_SITE_TITLE = "Crowd Safety Admin"
ADMIN_INDEX_TITLE = "Dashboard"

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

ADMIN_MEDIA_PREFIX = '/static/admin/'

# Custom admin site header
ADMIN_SITE_HEADER = "Crowd Safety Management System"
ADMIN_SITE_TITLE = "Crowd Safety Admin"
ADMIN_INDEX_TITLE = "Dashboard"

WSGI_APPLICATION = 'crowd_safety.wsgi.application'
ASGI_APPLICATION = 'crowd_safety.asgi.application'

# Database - Use SQLite without GIS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# Comment out Redis for now, use in-memory channel layer
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'accounts.User'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login/Logout URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Email settings (for alerts)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Use console for development
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'

# Twilio settings for SMS (optional)
TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
TWILIO_PHONE_NUMBER = ''

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Add this at the bottom of settings.py

# Gemini AI Configuration

# At the very bottom
GEMINI_API_KEY = "AIzaSyCb-hltBGfxzKkDdsVN-q5lxm6-VnG5N70"

# Admin customization
ADMIN_SITE_HEADER = "Crowd Safety Management System"
ADMIN_SITE_TITLE = "Crowd Safety Admin"
ADMIN_INDEX_TITLE = "Dashboard"

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Add at the bottom of settings.py

# Admin customization
ADMIN_SITE_HEADER = "Crowd Safety Management System"
ADMIN_SITE_TITLE = "Crowd Safety Admin"
ADMIN_INDEX_TITLE = "Dashboard"

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Replace with your real key # Replace with your actual key
