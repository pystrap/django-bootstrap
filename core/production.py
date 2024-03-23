from urllib.parse import urlparse

from .settings import *
import os

DEBUG = False
# Configure the domain name using the environment variable
# that Azure automatically creates for us.
ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []

# Configure Postgres database; the full username is username@servername,
# which we construct using the DBHOST value.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['DBNAME'],
        'HOST': os.environ['DBHOST'],
        'USER': os.environ['DBUSER'],
        'PASSWORD': os.environ['DBPASS'],
        'PORT': os.environ['DBPORT'],
        'OPTIONS': {'sslmode': 'require'},
    }
}


MEDIA_ROOT = "/storage"
ARTWORKS_DIR = os.path.join(MEDIA_ROOT, "artworks")
ENTITY_FILES_DIR = os.path.join(MEDIA_ROOT, "entity_files")
STORAGE_URL = os.environ['SAS_ENDPOINT']
AZURE_SAS_TOKEN = os.environ['SAS_TOKEN']

# DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
# # AZURE_LOCATION = 'artworks'
# AZURE_ACCOUNT_NAME = 'swandatastorage01'
# AZURE_CONTAINER = 'datastore01'
# AZURE_CONNECTION_STRING = os.environ['AZ_CONNECTION_STRING']

# Email configurations
EMAIL_SEND_EMAILS = True

EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_USE_TLS = bool(os.environ['EMAIL_USE_TLS'])
EMAIL_USE_SSL = bool(os.environ['EMAIL_USE_SSL'])

FRONTEND_APP_DIR = os.environ['FRONTEND_APP_DIR']
CORS_ALLOWED_ORIGINS = [
    f"{urlparse(FRONTEND_APP_DIR).scheme}://{urlparse(FRONTEND_APP_DIR).netloc}",
]
EXTERNAL_SOURCES_ARTIST_ID = 751

