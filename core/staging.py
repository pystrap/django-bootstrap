from urllib.parse import urlparse

from .settings import *
import os

DEBUG = True
# Configure the domain name using the environment variable
# that Azure automatically creates for us.

# ALLOWED_HOSTS = [ENV.get('WEBSITE_HOSTNAME')] if 'WEBSITE_HOSTNAME' in ENV else []
ALLOWED_HOSTS = ['.staging.qmodels.co.uk', 'staging.qmodels.co.uk']


MEDIA_ROOT = "/var/www/fastuser/data/www/_qmodels_media/staging"
ENTITY_FILES_DIR = os.path.join(MEDIA_ROOT, "entity_files")

# Email configurations
EMAIL_SEND_EMAILS = False


