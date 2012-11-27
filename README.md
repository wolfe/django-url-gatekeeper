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
        (r'^/login/', None),
        (r'^/logout/', None),
     )

    RESTRICTED_URLS = (
        r'^/semiprivate/public/',
    )

Meaning of RESTRICTED_URLS
-------------------------
Middleware component that wraps the permission_check decorator around
views for matching URL patterns. To use, add the class to
MIDDLEWARE\_CLASSES and define RESTRICTED\_URLS in your settings.py.
- All matching RESTRICTED\_URLS must be met.
- At least one RESTRICTED\_URLS must match.
- To exempt a URL from requiring permissions, use None

Each permission string can either be "None", a permission, or a
boolean property of a user.)

RESTRICTED_URLS_EXCEPTIONS
---------------------------
This is simply a list of patterns which are not subject to
RESTRICTED\_URLS.  This should only be used rarely.  The recommended
way to declare that a URL does not require permissions is to use a
permission specification of None in RESTRICTED\_URLS.   There are two
reasons why this feature is supplied:
1.  For backwards compatability
2.  To simplify what would otherwise be a complex set of patterns to
indicate that most of a set of URLs require the same permissions, but that
there are a few exceptions which are open.


Using TOKENS
-------------------------
To use tokens in URL which cause the URL to expire, two steps are
required:  Add the token to TOKEN\_REQUIRED\_URLS, and then be sure
that the token is added as a GET parameter to the link using, say:

    from url_gatekeeper import add_token
    return add_token('/temporary/?user=23', expiry=30) # (expiry defaults to 10 seconds)

The mechanism is useful for both "locking" the GET parameters at URL
generation as well as for presenting dynamic data which the user
should only view as it was mostly recently prepared.
