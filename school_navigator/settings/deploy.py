# Settings for live deployed environments: vagrant, staging, production, etc
from .base import *  # noqa

os.environ.setdefault('CACHE_HOST', '127.0.0.1:11211')
os.environ.setdefault('BROKER_HOST', '127.0.0.1:5672')

ENVIRONMENT = os.environ['ENVIRONMENT']

DEBUG = False

DATABASES['default']['NAME'] = 'school_navigator_%s' % ENVIRONMENT.lower()
DATABASES['default']['USER'] = 'school_navigator_%s' % ENVIRONMENT.lower()
DATABASES['default']['HOST'] = os.environ.get('DB_HOST', '')
DATABASES['default']['PORT'] = os.environ.get('DB_PORT', '')
DATABASES['default']['PASSWORD'] = os.environ.get('DB_PASSWORD', '')

WEBSERVER_ROOT = '/var/www/school_navigator/'

PUBLIC_ROOT = os.path.join(WEBSERVER_ROOT, 'public')

STATIC_ROOT = os.path.join(PUBLIC_ROOT, 'static')

MEDIA_ROOT = os.path.join(PUBLIC_ROOT, 'media')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '%(CACHE_HOST)s' % os.environ,
    }
}

EMAIL_HOST = "email-smtp.us-east-1.amazonaws.com"
EMAIL_HOST_USER = "AKIAJ7B33FCWH5FMSOBA"
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = '[School_Navigator %s] ' % ENVIRONMENT.title()
DEFAULT_FROM_EMAIL = 'noreply@%(DOMAIN)s' % os.environ
SERVER_EMAIL = DEFAULT_FROM_EMAIL

COMPRESS_ENABLED = True

SESSION_COOKIE_SECURE = True

SESSION_COOKIE_HTTPONLY = True

ALLOWED_HOSTS = [os.environ['DOMAIN']]

# Uncomment if using celery worker configuration
CELERY_SEND_TASK_ERROR_EMAILS = True
BROKER_URL = 'amqp://school_navigator_%(ENVIRONMENT)s:%(BROKER_PASSWORD)s@%(BROKER_HOST)s/school_navigator_%(ENVIRONMENT)s' % os.environ  # noqa

# Environment overrides
# These should be kept to an absolute minimum
if ENVIRONMENT.upper() == 'LOCAL':
    # Don't send emails from the Vagrant boxes
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ADMINS = (
    ('Code for Durham', 'school-inspector@googlegroups.com'),
)
MANAGERS = ADMINS

LOGGING['handlers']['file']['filename'] = '/var/www/school_navigator/log/schools.log'
