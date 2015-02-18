"""
Django settings for codeshop project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from decimal import Decimal


# === util for getting custom settings ===
def custom(key, default=None):
    try:
        custom = __import__('custom_settings')
        return getattr(custom, key)
    except:
        return default


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 't%npqx^5_0!tp4cd3vd1(r5yyguh)ins*iy5$_@0z*ld-n=ju-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if (custom('DEBUG') in [None, True]) else False

ALLOWED_HOSTS = custom('ALLOWED_HOSTS') or []
ADMINS = custom('ADMINS') or []

TEMPLATE_DEBUG = True


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',
    'social_auth',

    'extranet',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'codeshop.urls'

WSGI_APPLICATION = 'codeshop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_L10N = True

USE_TZ = True
TIME_ZONE = custom('TIME_ZONE', 'UTC')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = custom('STATIC_ROOT')


# === social auth tweaks ===
AUTHENTICATION_BACKENDS = (
    'social_auth.backends.google.GoogleOAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
)

GOOGLE_OAUTH2_CLIENT_ID = custom('GOOGLE_OAUTH2_CLIENT_ID')
GOOGLE_OAUTH2_CLIENT_SECRET = custom('GOOGLE_OAUTH2_CLIENT_SECRET')

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL = '/login-error/'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'social_auth.context_processors.social_auth_by_type_backends',
    'extranet.context_processors.global_settings',
    'extranet.context_processors.user_projects_and_teams',
)

SOCIAL_AUTH_ENABLED_BACKENDS = ('google')
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'


# === GITHUB ===
GITHUB_ACCESS_TOKEN = custom('GITHUB_ACCESS_TOKEN')


# === EMAIL ===
EMAIL_HOST = custom('EMAIL_HOST')
EMAIL_HOST_USER = custom('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = custom('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = custom('DEFAULT_FROM_EMAIL')
SERVER_EMAIL = custom('SERVER_EMAIL')

# === GLOBAL SETTINGS ===
SITE_NAME = custom('SITE_NAME') or 'My Codeshop'


# === time tracker ===
TIMER_STEPS = Decimal('4.0')  # th of 1h
TIMER_STEP_SIZE = int(Decimal('1.0') / TIMER_STEPS * 3600)
TIMER_HEADROOM = Decimal('12.0')  # th of 1h
