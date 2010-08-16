# Django settings for fryweb project.
import os
PROJECT_PATH = os.path.abspath(os.path.split(__file__)[0])

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Seb Bacon', 'seb.bacon@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'trevor'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, "media/")


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/resources/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'nsryqx^q8*0$2f8vdwm^_e0bawp=_c5(&$maleaix^exjzvain'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'trevor.loaders.load_template_source',
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'middleware.GoogleAnalyticsMiddleware',
    'facebook.djangofb.FacebookMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, "templates"),
    os.path.join(PROJECT_PATH, "casestudies", "templates"),
    
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "context_processors.flatpages",
    "context_processors.include_settings",
    "context_processors.debug"
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.admin',
    'south',
    'whatever',
    'holding',
    'facebooktrev',
    'manager'
)

AUTHENTICATION_BACKENDS = ('backends.NoAuthBackend',
                           'django.contrib.auth.backends.ModelBackend',
                           )

CURRENT_SEASON = 2010
CURRENT_LEAGUE_ID = '%d-%d Season (Current)' % (CURRENT_SEASON,
                                                CURRENT_SEASON+1)
PREVIOUS_LEAGUE_ID = '%d-%d Season (Final)' % (CURRENT_SEASON-1,
                                                CURRENT_SEASON)
OFFLINE = False
ACCOUNT_ACTIVATION_DAYS = 400

LOGIN_URL = '/login_form/'

CACHE_BACKED = 'locmem://?timeout=36000'
GOOGLE_ANALYTICS_ID = "UA-10089623-1"

STATIC_ROOT = os.path.join(PROJECT_PATH, "static_pages/")
TERMS = open(STATIC_ROOT + 'terms.txt').read()
PRIVACY = open(STATIC_ROOT + 'privacy.txt').read()

FACEBOOK_API_KEY = ""
FACEBOOK_SECRET_KEY = ""
FACEBOOK_APP_URL = "http://apps.facebook.com/whatevertrevor/"

SKIN_DIRECTORY = "plain"

CURRENT_COMPETITION_ID = 5 # the default competition entered on the
                           # home page
PREVIOUS_COMPETITION_ID = 2 
FIRST_COMPETITION_ID = 1
CLOSE_SEASON = True
CAMPAIGN_MONITOR_KEY = "744f528619f20ce0537a4b2cb6a0e879"
CAMPAIGN_MONITOR_LIST = "8b86d0c47ac402db792f58e504e9e5d0"
try:
    from local_settings import *
except ImportError:
    pass

