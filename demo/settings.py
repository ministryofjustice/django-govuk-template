import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # demo root
PROJECT_ROOT = os.path.dirname(BASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

SECRET_KEY = 'demo demo demo demo demo demo demo demo demo demo '
DEBUG = True
ALLOWED_HOSTS = ['*']

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = True
USE_TZ = True

WSGI_APPLICATION = 'wsgi.application'
ROOT_URLCONF = 'urls'
INSTALLED_APPS = [
    # standard django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # installed distribution
    'govuk_template_base',
]
if os.path.isdir(os.path.join(BASE_DIR, 'govuk_template')):
    INSTALLED_APPS += [
        # simulating inclusion once `startgovukapp` is called
        'govuk_template',
    ]
INSTALLED_APPS += [
    # this demo (not included in distribution)
    'demo_service',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'govuk_template_base.context_processors.govuk_template_base',
            ],
        },
    },
]
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite'),
    }
}
