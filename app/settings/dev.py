from .base import *

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',

        'NAME': 'Youtube_helper_Database',

        'USER': 'jaqb',

        'PASSWORD': 'jw8s0F4',

        'HOST': 'localhost',

        'PORT': '5432',
    }
}

STATIC_URL = '/static/'
