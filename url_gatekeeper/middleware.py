from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden
import re
from . import check_token

def permissions_required_with_403(perms, request):
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

    for perm in perms:
        if not _checkperm(request.user, perm):
            return HttpResponseForbidden("Requires permission %s" % perm)
    return None

class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to view any page other
    than those listed in settings.LOGIN_EXEMPT_URLS.

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.

    From http://djangosnippets.org/snippets/1179/
    """
    def __init__(self):
        self.exempt_urls = []
        self.LOGOUT_URL = settings.LOGOUT_URL
        if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
            self.exempt_urls += [re.compile(url) for url in settings.LOGIN_EXEMPT_URLS]

    def process_request(self, request):
        assert hasattr(request, 'user'), "The Login Required middleware\
 requires authentication middleware to be installed. Edit your\
 MIDDLEWARE_CLASSES setting to insert\
 'django.contrib.auth.middlware.AuthenticationMiddleware'. If that doesn't\
 work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
 'django.core.context_processors.auth'."

        if (request.user.is_authenticated()
            or any(m.match(request.path_info) for m in self.exempt_urls)):
            return
        elif request.path_info == self.LOGOUT_URL:
            return HttpResponseRedirect(self.login_url)
        else:
            return HttpResponseRedirect('%s?next=%s' % (settings.LOGIN_URL, request.path_info))

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
    def __init__(self):
        def setting(x): return getattr(settings, x, [])
        self.restricted = tuple([(re.compile(url[0]), url[1])
                                 for url in setting('RESTRICTED_URLS')])
        self.exceptions = tuple([re.compile(url)
                                 for url in setting('RESTRICTED_URLS_EXCEPTIONS')])

    def process_view(self, request, view_func, view_args, view_kwargs):
        # An exception match should immediately return None
        for path in self.exceptions:
            if path.match(request.path_info):
                return None

        # Requests matching a restricted URL pattern are returned
        # wrapped with the permission_required_with_403 decorator
        required_permissions = [perm for url,perm in self.restricted if url.match(request.path_info)]
        if required_permissions:
            required_permissions = [r for r in required_permissions if r is not None]
            return permissions_required_with_403(required_permissions, request)
        else:
            return HttpResponseForbidden(
                content= "No user can view url %s.  "
                         "There is no permission setting in RESTRICTED_URLS."
                % request.path_info)

class TokenRequiredMiddleware(object):
    def __init__(self):
        patterns = settings.TOKEN_REQUIRED_URLS
        self.token_required_urls = tuple([re.compile(url) for url in patterns])
    def process_request(self, request):
        for m in self.token_required_urls:
            if m.match(request.path_info):
                token = request.GET.get('url_token')
                if not (check_token(token, request.path_info)):
                    return HttpResponseForbidden("View cannot be bookmarked.")
