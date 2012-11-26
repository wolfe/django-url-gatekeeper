from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden
import re
from . import check_token
from django.contrib.auth.views import logout_then_login

def permissions_required_with_403(perms):
    """
    Works similar to django.contrib.auth.decorators.permission_required but
    (a) displays a 403.html template instead of redirecting to login, and
    (b) requires all permissions listed
    """
    def _checkperm(user, perm):
        return (user.has_perm(perm)
                or (perm == 'is_authenticated' and user.is_authenticated())
                # Handles, say, is_staff; insist on True so that we
                # don't inadvertently match a function.
                or (True == getattr(user, perm, None)))

    def dec(view_func):
        def checkperm(request, *args, **kwargs):
            for perm in perms:
                if not _checkperm(request.user, perm):
                    return HttpResponseForbidden("Requires permission %s" % perm)
            return view_func(request, *args, **kwargs)
        return checkperm
    return dec


class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.

    From http://djangosnippets.org/snippets/1179/
    """
    def __init__(self, _settings=settings):
        self.login_url = _settings.LOGIN_URL
        self.exempt_urls = [re.compile(self.login_url)]
        self.LOGOUT_URL = _settings.LOGOUT_URL
        if hasattr(_settings, 'LOGIN_EXEMPT_URLS'):
            self.exempt_urls += [re.compile(url) for url in _settings.LOGIN_EXEMPT_URLS]

    def process_request(self, request):
        if any(m.match(request.path_info) for m in self.exempt_urls):
            return

        assert hasattr(request, 'user'), "The Login Required middleware\
 requires authentication middleware to be installed. Edit your\
 MIDDLEWARE_CLASSES setting to insert\
 'django.contrib.auth.middlware.AuthenticationMiddleware'. If that doesn't\
 work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
 'django.core.context_processors.auth'."
        # HACK for IWK only:  The "Anonymous" user is not logged in.
        if not request.user.is_authenticated() or request.user.username == 'Anonymous':
            if not any(m.match(request.path_info) for m in self.exempt_urls):
                if request.user.username == 'Anonymous':
                    return logout_then_login(request)
                if request.path_info == self.LOGOUT_URL:
                    return HttpResponseRedirect(self.login_url)
                else:
                    return HttpResponseRedirect('%s?next=%s' % (self.login_url, request.path_info))

class RequirePermissionMiddleware(object):
    """
    Middleware component that wraps the permission_check decorator around
    views for matching URL patterns. To use, add the class to
    MIDDLEWARE_CLASSES and define RESTRICTED_URLS and
    RESTRICTED_URLS_EXCEPTIONS in your settings.py.

    URLs listed in RESTRICTED_URLS_EXCEPTIONS are exempt for checks by
    this middleware.  Otherwise,
       - All matching RESTRICTED_URLS must be met.
       - At least one RESTIRCTED_URLS must match.
    For example:

    RESTRICTED_URLS = (
                          (r'^/topsecet/$', 'auth.access_topsecet'),
                          (r'^/admin$', 'is_staff'),
                          (r'^/.*$', 'is_authenticated'),
                      )
    RESTRICTED_URLS_EXCEPTIONS = (
                          r'^/login/$',
                          r'^/logout/$',
                      )

    Adapted from http://djangosnippets.org/snippets/1219/
    """
    def __init__(self, _settings=settings):
        self.restricted = tuple([(re.compile(url[0]), url[1]) for url in _settings.RESTRICTED_URLS])
        self.exceptions = tuple([re.compile(url) for url in _settings.RESTRICTED_URLS_EXCEPTIONS])

    def process_view(self, request, view_func, view_args, view_kwargs):
        # An exception match should immediately return None
        for path in self.exceptions:
            if path.match(request.path_info): return None
        # Requests matching a restricted URL pattern are returned
        # wrapped with the permission_required_with_403 decorator
        required_permissions = [perm for url,perm in self.restricted if url.match(request.path_info)]
        if required_permissions:
            return permissions_required_with_403(required_permissions)(view_func)(request, *view_args, **view_kwargs)
        else:
            return HttpResponseForbidden(content="No user can currently view; no permission setting in RESTRICTED_URLS.")

class TokenRequiredMiddleware(object):
    def __init__(self, _settings=settings):
        patterns = _settings.TOKEN_REQUIRED_URLS
        self.token_required_urls = tuple([re.compile(url) for url in patterns])
    def process_request(self, request):
        for m in self.token_required_urls:
            if m.match(request.path_info):
                token = request.GET.get('url_token')
                if not (check_token(token, request.path_info)):
                    return HttpResponseForbidden("View cannot be bookmarked.")
