################################################################
# SEE LINES WITH COMMENT "ADD ME" FOR SAMPLE CONFIGS
################################################################

import os
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dev.db',
    }
}

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'url_gatekeeper.middleware.LoginRequiredMiddleware', # ADD ME
    'url_gatekeeper.middleware.TokenRequiredMiddleware', # (OPTIONALLY) ADD ME
    'url_gatekeeper.middleware.RequirePermissionMiddleware', # ADD ME
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'url_gatekeeper', # ADD ME
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, "templates"),
)


CACHES = {
 'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
 },
 'shared': { # ADD ME
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/django_cache',
 }
}

ROOT_URLCONF = 'example.urls'

LOGIN_URL = '/login/' # ADD ME
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/logout/' # ADD ME

LOGIN_EXEMPT_URLS = ( # ADD ME
    r'^/public/',
)
TOKEN_REQUIRED_URLS = ( # ADD ME
    r'^/dbfile/', # Same as '^/dbfile/.*$'
)
RESTRICTED_URLS = ( # ADD ME
    (r'^/private/', 'is_staff'),
    (r'^/semiprivate/', 'can_view_semiprivate'),
)
RESTRICTED_URLS_EXCEPTIONS = ( # ADD ME
    r'^/login/',
    r'^/logout/',
)


