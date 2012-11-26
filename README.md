django-url-gatekeeper
================

django-url-gatekeeper is an app with opt-out permissions based on URL
only.   This has the disadvantage of being less pythonic, but has the
advantages of default permission being "nobody" and a central list of
permissions.

Additionally, django-url-gatekeeper supplies an API for supplying a
one-use TOKEN to a URL pattern, making the view temporarily
admissible.

Usage
-----

See examples/settings.py for sample configurations.  In particular, in
settings.py you will need to add to INSTALLED_APPS:

    'url_gatekeeper',

and add any or all of the following MIDDLEWARE_CLASSES:

    'url_gatekeeper.middleware.LoginRequiredMiddleware',
    'url_gatekeeper.middleware.TokenRequiredMiddleware',
    'url_gatekeeper.middleware.RequirePermissionMiddleware',

If you choose to use TokenRequiredMiddleware, you will need to specify
a 'shared' cache which is shared across all threads.  For example:

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
        'shared': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/tmp/django_cache',
        }
    }

Lastly, configure the settings.  Here is a sample:

    LOGIN_URL = '/login/'
    LOGOUT_URL = '/logout/'
    LOGIN_EXEMPT_URLS = (
        r'^/public/',
    )
    TOKEN_REQUIRED_URLS = (
        r'^/report_on_last_view/',
    )
    RESTRICTED_URLS = (
        (r'^/private/', 'is_staff'),
        (r'^/semiprivate/', 'can_view_semiprivate'),
     )
    RESTRICTED_URLS_EXCEPTIONS = (
        r'^/login/',
        r'^/logout/',
    )
