from .base import *

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',

        'NAME': env("POSTGRES_DB"),

        'USER': env("POSTGRES_USER"),

        'PASSWORD': env("POSTGRES_PASSWORD"),

        'HOST': env("POSTGRES_HOST"),

        'PORT': env("POSTGRES_PORT"),
    }
}

# AWS S3 config

AWS_S3_HOST = 's3.eu-central-1.amazonaws.com'
AWS_S3_REGION_NAME="eu-central-1"
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN= f'{AWS_S3_HOST}/{env("AWS_STORAGE_BUCKET_NAME")}'
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'
AWS_QUERYSTRING_AUTH = False
AWS_HEADERS = {
    'Access-Control-Allow-Origin': f'{env("AWS_ALLOW_ORIGIN")}',
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STORAGES = {
    "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"}, 
    "staticfiles": {"BACKEND": "storages.backends.s3boto3.S3StaticStorage"},
}

STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'

MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'