from urllib.parse import urlparse

from .settings import *
import os

DEBUG = False
# Configure the domain name using the environment variable
# that Azure automatically creates for us.

# ALLOWED_HOSTS = [ENV.get('WEBSITE_HOSTNAME')] if 'WEBSITE_HOSTNAME' in ENV else []
ALLOWED_HOSTS = ['.qmodels.co.uk', 'qmodels.co.uk']

MEDIA_ROOT = "/var/www/fastuser/data/www/_qmodels_media"
ENTITY_FILES_DIR = os.path.join(MEDIA_ROOT, "entity_files")

# Email configurations
EMAIL_SEND_EMAILS = True


