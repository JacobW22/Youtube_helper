from .base import *

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',

        'NAME': os.environ.get("DB_NAME"),

        'USER': os.environ.get("DB_USERNAME"),

        'PASSWORD': os.environ.get("DB_PASSWORD"),

        'HOST': os.environ.get("DB_HOST"),

        'PORT': os.environ.get("DB_PORT"),
    }
}

# AWS S3 config

AWS_S3_HOST = 's3.eu-central-1.amazonaws.com'
AWS_S3_REGION_NAME="eu-central-1"
AWS_ACCESS_KEY_ID = os.environ.get("AWS_SECRET_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN= f'{AWS_S3_HOST}/{os.environ.get("AWS_STORAGE_BUCKET_NAME")}'
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'
AWS_QUERYSTRING_AUTH = False
AWS_HEADERS = {
    'Access-Control-Allow-Origin': f'{os.environ.get("AWS_ALLOW_ORIGIN")}',
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STORAGES = {
    "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"}, 
    "staticfiles": {"BACKEND": "storages.backends.s3boto3.S3StaticStorage"},
}

STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'

MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'